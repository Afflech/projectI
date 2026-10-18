# Bao Cao Audit Phase Docker Va Docker Desktop

Ngay lap bao cao: 2026-10-19

## 1. Muc Tieu Phase

Phase nay tap trung vao viec bien cach chay du an tu nhieu lenh thu cong thanh mot
workflow de quan ly hon bang Docker:

- Dong goi backend FastAPI va frontend Vite thanh container.
- Chay ca FE/BE bang Docker Compose.
- Them helper script de start/stop stack.
- Them helper cai Docker Engine tren Ubuntu.
- Them helper cai Docker Desktop GUI de quan ly container bang giao dien.
- Ghi tai lieu cach dung, cac context Docker va cac luu y ve port.

## 2. Ket Qua Da Hoan Thanh

### Docker Compose Cho Du An

Da them:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `backend/.dockerignore`
- `frontend/.dockerignore`
- `backend/requirements.docker.txt`

Compose hien co hai service:

- `backend`: chay FastAPI tren port `8000`, co healthcheck `/health`.
- `frontend`: chay Vite tren port `5173`, phu thuoc backend healthy.

Data backend duoc mount ra `backend/data/` de quan ly SQLite, uploads va vectors.

### Helper Scripts

Da them:

- `scripts/install-docker-ubuntu.sh`: cai Docker Engine va Docker Compose plugin bang
  Docker apt repository chinh thuc.
- `scripts/install-docker-desktop-ubuntu.sh`: tai va cai Docker Desktop `.deb` cho
  Ubuntu amd64.
- `scripts/docker-up.sh`: tao `backend/data`, truyen UID/GID, build va start Compose.
- `scripts/docker-down.sh`: stop Compose stack.

`docker-up.sh` va `docker-down.sh` co fallback `sg docker` neu user da duoc them vao
group `docker` nhung shell hien tai chua refresh group membership.

### Docker Desktop GUI

Da them tai lieu va installer helper cho Docker Desktop:

- Kiem tra Ubuntu/amd64.
- Cai prerequisites `ca-certificates`, `curl`, `gnome-terminal`.
- Tai `docker-desktop-amd64.deb`.
- Cai bang `sudo apt-get install`.
- Them user vao group `kvm` neu group ton tai.
- Nhac user log out/log in, mo Docker Desktop va accept terms.

## 3. Kiem Chung Da Thuc Hien

Kiem tra scripts:

```bash
bash -n scripts/install-docker-ubuntu.sh \
  scripts/install-docker-desktop-ubuntu.sh \
  scripts/docker-up.sh \
  scripts/docker-down.sh
```

Ket qua: passed.

Kiem tra Compose config:

```bash
docker compose config --quiet
```

Ket qua: passed trong Docker Desktop context.

Kiem tra Docker Engine stack truoc do:

- Backend container da tung start thanh cong va healthy.
- Frontend container da tung start thanh cong tren `5173`.
- `GET http://127.0.0.1:8000/health` tra `200`.
- `GET http://127.0.0.1:5173` tra `200`.
- CORS preflight tu `http://localhost:5173` tra `200`.
- Tao notebook qua Docker backend thanh cong.

Kiem tra Docker Desktop:

- `docker context show`: `desktop-linux`.
- `docker info` ngoai sandbox tra server Docker Desktop thanh cong.
- `docker compose config --quiet` passed trong Desktop context.
- Docker Desktop context hien chua co image/container project; stack da duoc stop de
  tranh port conflict.

Kiem tra KVM:

- `/dev/kvm` ton tai ngoai sandbox.
- Group `kvm` co user `quanhang`.
- Group `docker` co user `quanhang`.

## 4. Thay Doi Ky Thuat Quan Trong

### Docker Build Duoc Toi Uu Cho Demo Offline

Ban dau backend Dockerfile dung `backend/requirements.txt`, keo ca `faiss-cpu` va
`google-generativeai`. Lan build dau rat cham vi cac dependency nay lon va pip
backtracking lau.

Da tach `backend/requirements.docker.txt` gon hon:

- FastAPI/Uvicorn
- Pydantic
- pypdf
- requests
- numpy

Docker Compose dat mac dinh:

```yaml
LLM_PROVIDER: mock
```

Ly do:

- Demo Docker van chay duoc retrieval/citation bang NumPy fallback.
- Khong can Gemini key de demo MVP.
- Build nhanh hon va it loi network/dependency hon.

Neu can Gemini trong Docker, them `google-generativeai` vao
`backend/requirements.docker.txt`, rebuild va truyen `GEMINI_API_KEY`.

### Quan Ly File Ownership

Compose chay backend voi:

```yaml
user: "${DOCKER_UID:-1000}:${DOCKER_GID:-1000}"
```

`scripts/docker-up.sh` tu set:

```bash
DOCKER_UID=$(id -u)
DOCKER_GID=$(id -g)
```

Muc dich la tranh viec container tao file root-owned trong `backend/data/`.

## 5. Audit Findings

### Finding 1 - Docker Desktop Context Khac Docker Engine Context

Muc do: Medium.

Docker Desktop tao context rieng `desktop-linux`, con Docker Engine he thong dung
context `default`. Image/container giua hai context khong dung chung theo cach nguoi
dung thuong ky vong.

Tac dong:

- Stack da build trong Engine khong hien trong Docker Desktop GUI.
- Muon thay trong Docker Desktop, can active context `desktop-linux` va chay lai
  `./scripts/docker-up.sh`.

Khuyen nghi:

```bash
docker context use desktop-linux
./scripts/docker-up.sh
```

Neu muon quay ve Engine:

```bash
docker context use default
```

### Finding 2 - Co The Bi Port Conflict Neu Chay Ca Engine Va Desktop

Muc do: Medium.

Ca hai context deu co the bind port `5173` va `8000`. Neu Engine stack dang chay,
Desktop stack co the start fail vi port dang duoc dung.

Da xu ly:

- Da stop Engine stack bang `docker compose down`.
- Docs da ghi ro khong nen chay cung luc.

Khuyen nghi:

Truoc khi chay trong Docker Desktop:

```bash
docker compose down
```

### Finding 3 - Docker Desktop Can KVM Va User Session Moi

Muc do: Medium.

Docker Desktop can quyen voi `/dev/kvm`. May hien co KVM va user da nam trong group
`kvm`, nhung sau khi them group, Linux thuong can log out/log in de session nhan
membership moi.

Khuyen nghi:

- Log out/log in sau khi cai Docker Desktop.
- Neu Docker Desktop khong start, kiem tra:

```bash
ls -l /dev/kvm
groups
```

### Finding 4 - Docker Desktop Installer Download `.deb` Moi Nhat

Muc do: Low.

Script tai file Docker Desktop `.deb` moi nhat tu URL cua Docker. Tien loi cho setup,
nhung khong pin version/checksum.

Khuyen nghi:

- Chap nhan cho moi truong dev/demo.
- Neu can reproducible setup, pin URL version cu the va checksum.

### Finding 5 - Docker Image Demo Khong Co Gemini SDK Mac Dinh

Muc do: Low.

Docker image demo duoc toi uu cho mock provider. Neu user set `LLM_PROVIDER=gemini`
va `GEMINI_API_KEY` ma chua them `google-generativeai` vao requirements Docker, request
Gemini se loi import.

Khuyen nghi:

- De demo MVP: giu `LLM_PROVIDER=mock`.
- De test Gemini trong Docker: them `google-generativeai==0.8.3` vao
  `backend/requirements.docker.txt`, rebuild.

## 6. Cach Chay Sau Phase Nay

### Chay Bang Docker Desktop GUI

1. Mo Docker Desktop va accept terms.
2. Chon context Desktop:

```bash
docker context use desktop-linux
```

3. Chay stack:

```bash
./scripts/docker-up.sh
```

4. Mo app:

```text
http://localhost:5173
```

5. Dung stack:

```bash
./scripts/docker-down.sh
```

### Chay Bang Docker Engine He Thong

```bash
docker context use default
./scripts/docker-up.sh
```

## 7. Trang Thai Hien Tai

- Code Docker/Compose da commit va push.
- Docker Desktop installer helper da commit va push.
- Docker Desktop daemon hoat dong o context `desktop-linux`.
- Stack project hien dang stopped de tranh port conflict.
- Compose config hop le trong Desktop context.
- Repo dang sach tai thoi diem audit.

## 8. De Xuat Tiep Theo

Uu tien cao:

- Chay `./scripts/docker-up.sh` trong context `desktop-linux` va xac nhan stack hien
  trong Docker Desktop GUI.
- Chup screenshot Docker Desktop containers cho bao cao/demo neu can.

Uu tien trung binh:

- Them `Makefile` hoac npm-style aliases: `make up`, `make down`, `make logs`.
- Them script `scripts/docker-logs.sh`.
- Pin Docker Desktop version/checksum neu can reproducibility cao.

Chua can lam ngay:

- Docker production build voi Nginx/static frontend.
- Multi-stage backend image toi uu size.
- CI build Docker images.
