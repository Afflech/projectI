# Khung Tien Do He Thong - Mini NotebookLM

Tai lieu nay la khung dieu hanh du an tu luc khoi tao den khi hoan thien san pham demo/bao cao Project I. Moi tinh nang nen duoc gan ma, trang thai, tieu chi done va phase ro rang de bam theo trong cac lan phat trien tiep theo.

## 1. Trang Thai Tong Quan

Ngay cap nhat gan nhat: 2026-10-14

| Muc | Trang thai | Ghi chu |
| --- | --- | --- |
| Product scope | Da chot MVP | Mini NotebookLM cho sinh vien, hoi dap theo nguon co citation |
| Backend skeleton | Done | FastAPI import va smoke test service layer da qua |
| Frontend skeleton | Done co ban | React/Vite build thanh cong |
| RAG core | Done co ban | Text ingestion, chunking, retrieval, citation lookup da qua smoke test |
| LLM integration | In progress | Co Gemini provider + mock fallback, can test voi API key that |
| Evaluation | In progress | Co demo sources va 7 cau hoi manual trong `demo_sources/` |
| Report/demo | In progress | Da co checklist demo voi flow PDF/TXT/paste |

Quy uoc trang thai:

- `Planned`: da nam trong scope nhung chua lam.
- `In progress`: dang co code/tai lieu nhung chua dat Definition of Done.
- `Blocked`: bi chan boi dependency, quota, moi truong, hoac quyet dinh thiet ke.
- `Done`: da implement, da test muc can thiet, da co ghi chu su dung.
- `Cut`: cat khoi scope Project I hien tai.

## 2. Phase Roadmap

### Phase 0 - Khoi Tao Du An

Muc tieu: chot bai toan, scope, stack va cau truc repo.

Thoi luong goi y: 2-3 ngay

Cong viec:

- `P0-01`: Viet mo ta bai toan, nguoi dung, muc tieu san pham.
- `P0-02`: Chot MVP va 1-2 tinh nang mo rong.
- `P0-03`: Chot stack: FastAPI, SQLite, React/Vite, vector search, Gemini provider.
- `P0-04`: Tao cau truc `backend/`, `frontend/`, `docs/`, `eval/`.
- `P0-05`: Tao README, env example, gitignore, huong dan run.

Tieu chi done:

- Repo co the cai dat theo README.
- Co tai lieu thiet ke ban dau.
- Scope khong mo rong ngoai MVP neu chua co ly do ro.

Trang thai hien tai: `Done co ban`

### Phase 1 - Nen Tang Backend Va Du Lieu

Muc tieu: co API va database du de quan ly notebook, source, message.

Thoi luong goi y: 1 tuan

Cong viec:

- `BE-01`: Tao SQLite schema cho `notebooks`, `sources`, `chunks`, `messages`, `notes`.
- `BE-02`: API CRUD notebook: create, list, rename, delete.
- `BE-03`: API source: upload file, paste text, list, toggle enabled, delete.
- `BE-04`: API message: list history theo notebook.
- `BE-05`: Xu ly status source: `pending`, `processing`, `ready`, `failed`.
- `BE-06`: Chuan hoa error response cho cac case notebook/source khong ton tai.

Tieu chi done:

- Tao/xoa/doi ten notebook hoat dong qua API.
- Them/xoa/bat/tat source hoat dong qua API.
- DB khong bi loi foreign key khi xoa notebook/source.
- Co test manual bang curl hoac script API.

Trang thai hien tai: `Done co ban`

### Phase 2 - Ingestion Pipeline

Muc tieu: nap nguon thanh text, chunk, metadata va vector.

Thoi luong goi y: 1-1.5 tuan

Cong viec:

- `ING-01`: Extract text tu PDF, giu so trang.
- `ING-02`: Extract text tu TXT/MD va pasted text.
- `ING-03`: Chunking 256-384 token, co overlap.
- `ING-04`: Tao hash file/text de cache va tranh trung lap.
- `ING-05`: Tao embedding cho chunk, dung prefix `passage:`.
- `ING-06`: Luu chunk metadata: source, page, text, vector_id.
- `ING-07`: Xu ly source failed neu PDF scan/khong co text.
- `ING-08`: Chay ingestion nen va cap nhat status tren UI.

Tieu chi done:

- Upload PDF co text tao duoc chunk kem page.
- Upload TXT/MD va paste text tao duoc chunk.
- Source loi hien `failed` kem message.
- Co the doi chunk size/overlap qua env.

Trang thai hien tai: `Done co ban - PDF text source da duoc smoke test voi page metadata`

### Phase 3 - Retrieval Va Citation

Muc tieu: tim dung chunk lien quan trong cac source dang bat va tra citation bam duoc.

Thoi luong goi y: 1 tuan

Cong viec:

- `RAG-01`: Embed question voi prefix `query:`.
- `RAG-02`: Tim top-k chunk bang cosine/FAISS.
- `RAG-03`: Loc ket qua theo notebook va source `enabled`.
- `RAG-04`: Tra ve score, chunk_id, source_id, source_title, page.
- `RAG-05`: API `GET /chunks/{id}` de xem doan goc.
- `RAG-06`: UI citation chips, bam vao hien evidence panel.
- `RAG-07`: Kiem tra disabled source khong duoc truy xuat.

Tieu chi done:

- Chat voi source enabled tra citations dung source.
- Tat source thi source do khong xuat hien trong retrieval.
- Citation bam duoc va hien doan goc + page.
- Co it nhat 5 cau hoi test tay qua nhieu source.

Trang thai hien tai: `Done co ban - PDF citation page metadata da duoc smoke test`

### Phase 4 - LLM Answering

Muc tieu: ghep prompt va goi LLM de tra loi chi dua tren context.

Thoi luong goi y: 1 tuan

Cong viec:

- `LLM-01`: Tao lop `LLMProvider` tach provider khoi business logic.
- `LLM-02`: Gemini Flash provider doc key tu env.
- `LLM-03`: Mock provider/fallback khi khong co key hoac demo offline.
- `LLM-04`: Prompt yeu cau chi tra loi tu context, neu thieu thi noi khong du thong tin.
- `LLM-05`: Yeu cau model chen marker citation `[chunk:id]`.
- `LLM-06`: Retry/backoff khi gap rate limit/quota tam thoi.
- `LLM-07`: Luu answer va citations vao `messages`.

Tieu chi done:

- Co the demo voi Gemini key that.
- Khi khong co key van test duoc retrieval/citation.
- Cau tra loi khong tu che khi context khong co thong tin.
- History luu lai user va assistant message.

Trang thai hien tai: `In progress - mock provider da qua smoke test, can Gemini key`

### Phase 5 - Frontend MVP

Muc tieu: giao dien dung duoc cho demo thuc te.

Thoi luong goi y: 1-1.5 tuan

Cong viec:

- `FE-01`: Layout 3 cot: source, chat, evidence/summary.
- `FE-02`: Notebook switcher, create, rename, delete.
- `FE-03`: Upload source PDF/TXT/MD.
- `FE-04`: Paste text source.
- `FE-05`: Source list co status, enable/disable, delete.
- `FE-06`: Chat composer, loading state, error state.
- `FE-07`: Render chat history va citation chips.
- `FE-08`: Evidence panel hien chunk text va page.
- `FE-09`: Responsive layout cho man hinh nho.

Tieu chi done:

- Demo duoc toan bo flow tu tao notebook den hoi dap co citation.
- UI khong vo layout o desktop va mobile co ban.
- Co loading/error state cho upload, ingest, chat.

Trang thai hien tai: `Done co ban - Vite build thanh cong, can chay browser checklist tren may demo`

### Phase 6 - Tinh Nang Mo Rong

Muc tieu: tang gia tri san pham nhung khong lam vo MVP.

Thoi luong goi y: 1 tuan

Uu tien chinh:

- `EXT-01`: Tom tat tung source sau ingestion.
- `EXT-02`: Goi y cau hoi hoc tap cho tung source.

Co the lam neu con thoi gian:

- `EXT-03`: Luu cau tra loi thanh note.
- `EXT-04`: Tao FAQ/study guide cho notebook.
- `EXT-05`: Ho tro DOCX.
- `EXT-06`: Them URL ingestion.

Tieu chi done:

- Summary/gợi y cau hoi hien tren UI sau khi source ready.
- Tinh nang mo rong khong lam cham hoac lam loi flow chat MVP.
- Neu lam notes/study guide thi co API, UI va data persistence ro rang.

Trang thai hien tai: `In progress nhe`

### Phase 7 - Chat Luong, Bao Mat Va Do On Dinh

Muc tieu: san pham du on cho demo va nop bai.

Thoi luong goi y: 1 tuan

Cong viec:

- `QA-01`: Validate file type va gioi han size upload.
- `QA-02`: Xu ly PDF scan/khong extract duoc text.
- `QA-03`: Xu ly LLM quota/API error bang fallback ro rang.
- `QA-04`: Khong log API key, khong commit `.env`.
- `QA-05`: Test xoa notebook/source khong de du lieu rac.
- `QA-06`: Kiem tra CORS, port, env setup.
- `QA-07`: Kiem tra UI tren Chrome desktop va mobile width.

Tieu chi done:

- Co checklist demo.
- Cac loi pho bien co message de hieu.
- Chay lai tu clone moi theo README duoc.

Trang thai hien tai: `In progress - da co checklist demo va failed-source message tren UI`

### Phase 8 - Evaluation Va Bao Cao

Muc tieu: co so lieu, nhan xet va tai lieu bao ve.

Thoi luong goi y: 1 tuan

Cong viec:

- `EVAL-01`: Tao bo 20-30 cau hoi trong `eval/`.
- `EVAL-02`: Gan expected source/page/evidence cho tung cau.
- `EVAL-03`: Viet script do top-k hit rate.
- `EVAL-04`: So sanh chunk size 256, 384, 512.
- `EVAL-05`: Neu kip, so sanh embedding fallback/e5-small/e5-base.
- `DOC-01`: Viet bao cao: bai toan, yeu cau, thiet ke, cong nghe.
- `DOC-02`: Ve so do RAG flow va data model.
- `DOC-03`: Viet han che: PDF scan, bang bieu, quota API, embedding CPU.
- `DOC-04`: Chuan bi slide va kich ban demo.
- `DOC-05`: Chuan bi cau hoi van dap va cau tra loi ngan.

Tieu chi done:

- Bao cao co so lieu danh gia retrieval.
- Slide co flow demo ro.
- Co danh sach rui ro va cach xu ly khi demo loi.

Trang thai hien tai: `Planned`

### Phase 9 - Release Demo

Muc tieu: chot ban nop bai va demo on dinh.

Thoi luong goi y: 2-3 ngay

Cong viec:

- `REL-01`: Freeze scope, khong them feature moi truoc demo.
- `REL-02`: Tao du lieu demo: 2-3 notebooks, 3-5 sources.
- `REL-03`: Kiem tra flow demo tu may sach.
- `REL-04`: Chuan bi `.env` rieng cho demo.
- `REL-05`: Chuan bi provider fallback neu Gemini quota loi.
- `REL-06`: Tag/backup ban nop.

Tieu chi done:

- Mo app, nap source, chat, citation deu chay trong 5-7 phut demo.
- Co video/screenshot backup.
- Co ban code va bao cao dong goi.

Trang thai hien tai: `Planned`

## 3. Feature Backlog Theo Nhom

### Notebook Management

| ID | Tinh nang | Uu tien | Trang thai |
| --- | --- | --- | --- |
| NB-01 | Tao notebook | P0 | In progress |
| NB-02 | Doi ten notebook | P0 | In progress |
| NB-03 | Xoa notebook | P0 | In progress |
| NB-04 | Luu notebook dang chon | P2 | Planned |

### Source Management

| ID | Tinh nang | Uu tien | Trang thai |
| --- | --- | --- | --- |
| SRC-01 | Upload PDF | P0 | In progress |
| SRC-02 | Upload TXT/MD | P0 | In progress |
| SRC-03 | Paste text | P0 | In progress |
| SRC-04 | URL ingestion | P2 | Planned |
| SRC-05 | DOCX ingestion | P2 | Planned |
| SRC-06 | Toggle enabled source | P0 | In progress |
| SRC-07 | Delete source | P0 | In progress |

### RAG Core

| ID | Tinh nang | Uu tien | Trang thai |
| --- | --- | --- | --- |
| RAG-01 | Extract text giu page | P0 | In progress |
| RAG-02 | Chunking co overlap | P0 | In progress |
| RAG-03 | Embedding local | P0 | In progress |
| RAG-04 | FAISS/vector search | P0 | In progress |
| RAG-05 | Filter theo enabled source | P0 | In progress |
| RAG-06 | Citation chunk detail | P0 | In progress |

### Chat

| ID | Tinh nang | Uu tien | Trang thai |
| --- | --- | --- | --- |
| CHAT-01 | Chat theo notebook | P0 | In progress |
| CHAT-02 | Luu lich su chat | P0 | In progress |
| CHAT-03 | Answer with citations | P0 | In progress |
| CHAT-04 | Empty-context answer | P0 | In progress |
| CHAT-05 | Retry/backoff LLM | P1 | Planned |

### Extensions

| ID | Tinh nang | Uu tien | Trang thai |
| --- | --- | --- | --- |
| EXT-01 | Tom tat source | P1 | In progress |
| EXT-02 | Goi y cau hoi | P1 | In progress |
| EXT-03 | Save answer as note | P2 | Planned |
| EXT-04 | Study guide/FAQ | P2 | Planned |

## 4. Quy Trinh Lam Viec Hang Tuan

Moi tuan nen co 4 viec co dinh:

1. Planning: chon 5-8 task nho tu roadmap, uu tien task dang chan demo.
2. Build: implement theo task, commit nho, khong tron qua nhieu feature.
3. Verify: test manual flow va ghi loi vao backlog.
4. Report: cap nhat trang thai trong tai lieu nay va viet 3-5 dong ket qua tuan.

Mau cap nhat tuan:

```md
## Week N - YYYY-MM-DD

Muc tieu:
- ...

Da lam:
- ...

Dang bi chan:
- ...

Tuan sau:
- ...
```

## 5. Definition Of Done

Mot tinh nang duoc danh dau `Done` khi dat cac dieu kien sau:

- Co API/UI hoac tai lieu tuong ung theo scope.
- Da test manual flow thanh cong.
- Co error/loading/empty state neu lien quan user.
- Khong lam hong flow chinh: tao notebook, them source, chat, xem citation.
- README hoac docs duoc cap nhat neu cach dung thay doi.

## 6. Risk Log

| Rui ro | Anh huong | Giam thieu |
| --- | --- | --- |
| Het quota Gemini khi demo | Chat that bai | Mock fallback, provider abstraction, chuan bi key du phong |
| PDF scan khong co text | Ingestion failed | Hien loi ro, ghi han che trong bao cao, OCR de future work |
| Embedding chat luong thap | Retrieval kem | Nang len multilingual-e5-small/fastembed khi moi truong san sang |
| CPU cham | Demo lau | Chay ingestion truoc, batch/caching theo file_hash |
| Scope phinh to | Tre tien do | Freeze P0 truoc, EXT chi lam sau khi MVP on |
| Moi truong cai package loi | Khong demo duoc | Chuan bi venv/node_modules truoc ngay demo, co screenshot/video backup |

## 7. Kich Ban Demo Chuan

1. Mo app va tao notebook moi.
2. Upload 1 PDF co text va paste 1 doan text ngan.
3. Doi ten notebook.
4. Doi enabled source de cho thay truy van bi gioi han theo nguon.
5. Dat cau hoi co dap an ro trong source.
6. Bam citation de hien doan goc va page.
7. Xem summary/goi y cau hoi cua source.
8. Mo chat history sau khi refresh.

## 8. Nguyen Tac Chot Scope

- P0 la bat buoc de nop MVP.
- P1 chi lam khi P0 da demo duoc end-to-end.
- P2 la optional, khong duoc lam cham bao cao va evaluation.
- Neu co bug anh huong demo, uu tien sua bug hon them tinh nang.
- Moi thay doi lon phai cap nhat lai roadmap nay.
