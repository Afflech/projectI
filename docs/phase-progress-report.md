# Bao Cao Tien Do Theo Phase - Mini NotebookLM

Ngay lap bao cao: 2026-10-14

## 1. Tong Quan

Trong cac phase vua qua, du an da di tu skeleton ban dau thanh mot MVP co the demo
duoc voi du lieu that. San pham hien tai cho phep sinh vien tao notebook, them tai
lieu PDF/TXT/MD hoac pasted text, hoi dap tren cac source dang bat, va bam citation
de xem lai doan evidence goc. Backend, frontend, ingestion, retrieval, citation va
demo checklist deu da co moc kiem chung co the lap lai.

Muc tieu lon nhat cua dot vua roi la chuyen trang thai tu "qua smoke test ky thuat"
sang "co the demo bang tai lieu that". Ket qua dat duoc gom: bo demo sources, smoke
test PDF co page metadata, checklist demo tren browser, va sua loi CORS khi Vite doi
sang port khac.

## 2. Cac Moc Commit Chinh

| Commit | Noi dung |
| --- | --- |
| `f9c824f` | Khoi tao Mini NotebookLM scaffold |
| `ef6f46a` | Them helper Git local cho workspace |
| `33f65da` | Them workflow smoke test MVP |
| `e73c1af` | Kiem chung MVP voi real demo sources |
| `a541525` | Sua CORS preflight cho dev origins/ports |

## 3. Ket Qua Theo Phase

### Phase 0 - Khoi Tao Du An

Trang thai: Done co ban.

Da hoan thanh:

- Chot scope MVP: ung dung Mini NotebookLM phuc vu hoc tap, hoi dap dua tren nguon
  tai lieu cua notebook.
- Chot stack: FastAPI, SQLite, React/Vite, local vector search, Gemini provider
  abstraction va mock fallback.
- Tao cau truc du an gom `backend/`, `frontend/`, `docs/`, `eval/`, `demo_sources/`.
- Co README huong dan chay backend/frontend va giai thich che do mock khi chua co
  `GEMINI_API_KEY`.

Gia tri dat duoc:

- Du an co nen tang ro de phat trien va bao cao.
- Scope MVP duoc giu gon, chua mo rong sang URL, DOCX, study guide hay notes.

### Phase 1 - Nen Tang Backend Va Du Lieu

Trang thai: Done co ban.

Da hoan thanh:

- Tao SQLite schema cho `notebooks`, `sources`, `chunks`, `messages`, `notes`.
- Co API tao, liet ke, doi ten, xoa notebook.
- Co API upload source PDF/TXT/MD, tao pasted text source, bat/tat source va xoa
  source.
- Co API lay chat history theo notebook.
- Source co status `pending`, `processing`, `ready`, `failed`.

Da kiem chung:

- Backend smoke test tao notebook, ingest source, chat, luu history va lay citation.
- Flow HTTP local da kiem tra upload PDF/MD, paste source, chat va disable source.

### Phase 2 - Ingestion Pipeline

Trang thai: Done co ban voi PDF text source.

Da hoan thanh:

- PDF ingestion dung `pypdf` de extract text va luu page number bat dau tu 1.
- TXT/MD va pasted text duoc doc thanh source text.
- Chunking co overlap, cau hinh qua `CHUNK_TOKENS` va `CHUNK_OVERLAP`.
- Tao file hash cho source va luu chunk metadata gom `source_id`, `page`, `text`,
  `vector_id`.
- Source khong co text extractable se chuyen sang `failed` voi message loi.

Da kiem chung:

- Them PDF demo 2 trang trong `demo_sources/project_i_rag_notes.pdf`.
- Smoke test moi assert PDF source `ready` va chunks co page `[1, 2]`.
- UI source list hien them loi khi ingestion failed.

Han che:

- PDF scan/image-only chua co OCR.
- PDF fixture hien la PDF text toi gian; nen harden bang `.gitattributes` `*.pdf binary`
  hoac tao fixture tu script neu can chay tren nhieu moi truong.

### Phase 3 - Retrieval Va Citation

Trang thai: Done co ban.

Da hoan thanh:

- Cau hoi duoc embed voi prefix `query:`.
- Chunk duoc embed voi prefix `passage:`.
- Vector search dung FAISS neu co, fallback NumPy cosine.
- Retrieval loc theo notebook va chi lay source dang `enabled` + `ready`.
- Chat response tra citation gom `chunk_id`, `source_id`, `source_title`, `page`,
  `quote`.
- API `GET /chunks/{id}` cho evidence panel.
- UI co citation chip; bam citation hien source title, page va chunk text.

Da kiem chung:

- Smoke test xac nhan disabled source khong duoc retrieve va khong duoc cite.
- Flow HTTP local xac nhan PDF citation co page 2 va lay chunk detail thanh cong.
- Flow HTTP local xac nhan sau khi tat pasted source, cau tra loi moi khong cite
  source do nua.

### Phase 4 - LLM Answering

Trang thai: In progress.

Da hoan thanh:

- Co lop provider tach logic LLM khoi business logic.
- Co Gemini provider doc key/model tu env.
- Co mock fallback de demo offline hoac khi chua co API key.
- Prompt yeu cau tra loi dua tren context va chen marker citation `[chunk:id]`.
- Assistant answer va citation JSON duoc luu vao `messages`.

Da kiem chung:

- Mock provider da qua smoke test va flow demo retrieval/citation.

Con thieu:

- Chua kiem chung chat quality voi Gemini key that.
- Chua co retry/backoff day du cho quota/rate-limit.

### Phase 5 - Frontend MVP

Trang thai: Done co ban.

Da hoan thanh:

- Layout 3 cot: sources, chat, evidence/summary.
- Tao, chon, doi ten va xoa notebook.
- Upload PDF/TXT/MD va paste text source.
- Source list co status, enable/disable va delete.
- Chat composer co loading state.
- Render chat history va citation chips.
- Evidence panel hien chunk text va page.
- Responsive layout co ban cho man hinh nho.

Da kiem chung:

- `npm run build` thanh cong.
- Flow API tuong duong browser da chay qua end-to-end.
- Da sua CORS de frontend van goi backend duoc khi Vite doi port tu `5173` sang
  `5174` hoac port dev local khac.

Can kiem tra tiep:

- Chay manual browser checklist bang Chrome tren may demo.
- Quan sat layout khi source error qua dai, citation nhieu hoac mobile width hep.

### Phase 6 - Tinh Nang Mo Rong

Trang thai: In progress nhe.

Da co:

- Sau ingestion, he thong goi summary prompt cho source.
- UI co khu vuc summary va suggested questions trong detail panel.

Chua lam trong sprint nay:

- Saved notes.
- Study guide/FAQ tu dong.
- DOCX ingestion.
- URL ingestion.

Ly do chua lam:

- Sprint vua roi uu tien do on dinh demo va citation voi du lieu that hon them tinh
  nang moi.

### Phase 7 - Chat Luong, Bao Mat Va Do On Dinh

Trang thai: In progress.

Da hoan thanh:

- Co checklist demo tai `docs/demo-checklist.md`.
- Upload chi cho phep PDF/TXT/MD.
- Source failed hien error message de de debug.
- `.env` khong duoc commit; `.env.example` co bien cau hinh can thiet.
- Da sua CORS preflight cho dev origins/ports.
- Backend smoke test va frontend build chay duoc lap lai.

Rui ro con lai:

- Chua co gioi han kich thuoc upload.
- Chua co OCR cho PDF scan.
- Chua co test tu dong cho UI bang browser.
- Chua co script cleanup data demo cu.

### Phase 8 - Evaluation Va Bao Cao

Trang thai: In progress.

Da hoan thanh:

- Tao `demo_sources/` gom:
  - `project_i_rag_notes.pdf`
  - `demo-study-notes.md`
  - `pasted-text-sample.txt`
  - `demo-questions.json`
- Co 7 cau hoi manual voi expected source/page/evidence.
- Co tai lieu nay de tong hop tien do phase.

Chua hoan thanh:

- Chua co bo 20-30 cau hoi evaluation.
- Chua co script do top-k hit rate.
- Chua so sanh chunk size 256/384/512.
- Chua co so lieu retrieval metrics cho bao cao cuoi.

### Phase 9 - Release Demo

Trang thai: Planned.

Da chuan bi:

- Repo da push len GitHub remote `Afflech/projectI`.
- Co demo checklist va demo sources.
- Backend/frontend co lenh run ro rang.

Can lam truoc ngay demo:

- Freeze scope.
- Chay checklist tren mot workspace sach.
- Chuan bi `.env` demo rieng neu dung Gemini key.
- Chuan bi fallback mock provider khi quota/API key gap loi.
- Tao screenshot/video backup.

## 4. Kiem Chung Da Thuc Hien

Backend:

```bash
cd backend
.venv/bin/python scripts/smoke_test.py
```

Ket qua: passed.

Frontend:

```bash
cd frontend
npm run build
```

Ket qua: passed.

CORS preflight:

- `OPTIONS /notebooks` tra `200` voi `http://localhost:5173`.
- `OPTIONS /notebooks` tra `200` voi `http://127.0.0.1:5173`.
- `OPTIONS /notebooks` tra `200` voi `http://0.0.0.0:5173`.
- `OPTIONS /notebooks` tra `200` voi `http://localhost:5174`.

Flow local:

- Tao notebook.
- Upload PDF demo va MD demo.
- Paste text demo.
- Doi source sang `ready`.
- Hoi cau co dap an trong PDF.
- Citation mo dung chunk va co page number.
- Disable pasted source.
- Hoi lai va xac nhan source da tat khong con duoc cite.
- History luu du cac message.

## 5. Danh Gia Hien Tai

MVP hien tai da dat muc "demo duoc bang tai lieu that" cho flow cot loi:

1. Tao notebook.
2. Them source PDF/TXT/MD/paste.
3. Ingest source thanh chunks co metadata.
4. Hoi dap dua tren source dang bat.
5. Tra ve citation.
6. Bam citation de xem evidence goc.
7. Tat source va thay doi ket qua retrieval.
8. Refresh van giu du lieu notebook/source/messages.

Chat quality voi Gemini that va evaluation dinh luong van la phan can tiep tuc lam.
Neu bao ve MVP, nen trinh bay ro rang rang mock provider chi la fallback demo offline;
gia tri ky thuat chinh da kiem chung la ingestion, retrieval, citation va source
filtering.

## 6. De Xuat Viec Tiep Theo

Uu tien cao:

- Chay manual checklist tren browser that va chup screenshot cac man hinh chinh.
- Them `.gitattributes` de danh dau `*.pdf binary`.
- Tao 20-30 cau hoi evaluation va script tinh top-k hit rate.
- Test voi Gemini API key that, ghi lai nhan xet ve chat quality.

Uu tien trung binh:

- Them upload size limit va message loi than thien hon.
- Them Playwright/manual UI regression cho luong demo.
- Them nut clear demo data hoac huong dan reset SQLite.
- Cai thien render error source neu message qua dai.

Cat khoi sprint hien tai:

- DOCX ingestion.
- URL ingestion.
- Notes/study guide nang cao.
- OCR cho PDF scan.
