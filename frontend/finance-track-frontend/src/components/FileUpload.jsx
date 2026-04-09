// src/components/FileUpload.jsx
// Загрузка, список, скачивание и удаление файлов транзакции

import { useEffect, useRef, useState } from "react";
import { FileAPI } from "../api";

// ─── Константы (должны совпадать с бэкендом) ─────────────────────────────────
const ALLOWED_TYPES = [
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp",
  "application/pdf",
  "text/csv",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
];
const MAX_MB    = 10;
const MAX_BYTES = MAX_MB * 1024 * 1024;

// ─── Вспомогательные функции ──────────────────────────────────────────────────
function fileIcon(contentType) {
  if (contentType.startsWith("image/"))       return "🖼";
  if (contentType === "application/pdf")      return "📄";
  if (contentType === "text/csv")             return "📊";
  return "📎";
}

function fmtSize(bytes) {
  if (bytes < 1024)            return `${bytes} Б`;
  if (bytes < 1024 * 1024)    return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

function fmtDate(iso) {
  return new Date(iso).toLocaleDateString("ru-RU");
}

// ─── Компонент ────────────────────────────────────────────────────────────────
export default function FileUpload({ transactionId }) {
  const [files, setFiles]               = useState([]);
  const [loading, setLoading]           = useState(true);
  const [uploading, setUploading]       = useState(false);
  const [uploadingName, setUploadingName] = useState("");
  const [uploadError, setUploadError]   = useState(null);
  const inputRef = useRef(null);

  // Загружаем список файлов
  const loadFiles = async () => {
    try {
      const data = await FileAPI.list(transactionId);
      setFiles(data);
    } catch {
      setFiles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [transactionId]);

  // ── Загрузка файла ──────────────────────────────────────────────────────────
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Клиентская валидация типа
    if (!ALLOWED_TYPES.includes(file.type)) {
      setUploadError(
        `Тип файла "${file.type}" не разрешён. Допустимы: JPEG, PNG, GIF, WEBP, PDF, CSV, XLSX`
      );
      return;
    }

    // Клиентская валидация размера
    if (file.size > MAX_BYTES) {
      setUploadError(
        `Файл слишком большой (${fmtSize(file.size)}). Максимум: ${MAX_MB} МБ`
      );
      return;
    }

    setUploadError(null);
    setUploading(true);
    setUploadingName(file.name);

    try {
      await FileAPI.upload(transactionId, file);
      await loadFiles();
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
      setUploadingName("");
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  // ── Скачивание ──────────────────────────────────────────────────────────────
  const handleDownload = async (fileId, fileName) => {
    try {
      const { url } = await FileAPI.downloadUrl(fileId);
      // Открываем в новой вкладке — браузер скачает или отобразит
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.click();
    } catch (err) {
      alert(`Ошибка при получении ссылки: ${err.message}`);
    }
  };

  // ── Удаление ────────────────────────────────────────────────────────────────
  const handleDelete = async (fileId, fileName) => {
    if (!confirm(`Удалить файл "${fileName}"?`)) return;
    try {
      await FileAPI.delete(fileId);
      setFiles((prev) => prev.filter((f) => f.id !== fileId));
    } catch (err) {
      alert(`Ошибка при удалении: ${err.message}`);
    }
  };

  return (
    <div>
      <h3 className="text-base font-semibold text-gray-800 mb-3 flex items-center gap-2">
        📎 Прикреплённые файлы
        <span className="bg-gray-100 text-gray-600 text-xs font-bold px-2 py-0.5 rounded-full">
          {files.length}
        </span>
      </h3>

      {/* ── Зона загрузки ── */}
      <div
        onClick={() => !uploading && inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center transition group
          ${uploading
            ? "border-indigo-300 bg-indigo-50 cursor-wait"
            : "border-gray-300 hover:border-indigo-400 hover:bg-indigo-50/30 cursor-pointer"
          }`}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={ALLOWED_TYPES.join(",")}
          onChange={handleFileChange}
          disabled={uploading}
        />

        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
            <p className="text-sm text-indigo-600 font-medium">
              Загружаю «{uploadingName}»…
            </p>
          </div>
        ) : (
          <>
            <p className="text-3xl mb-2 group-hover:scale-110 transition-transform select-none">
              ⬆️
            </p>
            <p className="text-sm font-medium text-gray-700">
              Нажмите для выбора файла
            </p>
            <p className="text-xs text-gray-400 mt-1">
              JPEG, PNG, GIF, WEBP, PDF, CSV, XLSX · макс. {MAX_MB} МБ
            </p>
          </>
        )}
      </div>

      {/* ── Ошибка загрузки ── */}
      {uploadError && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-start gap-2">
          <span className="shrink-0">⚠️</span>
          <span>{uploadError}</span>
          <button
            onClick={() => setUploadError(null)}
            className="ml-auto text-red-400 hover:text-red-600 shrink-0"
          >
            ✕
          </button>
        </div>
      )}

      {/* ── Список файлов ── */}
      {loading ? (
        <p className="text-center text-sm text-gray-400 mt-4">Загружаю список…</p>
      ) : files.length === 0 ? (
        <p className="text-center text-sm text-gray-400 mt-4">
          Файлов пока нет
        </p>
      ) : (
        <ul className="mt-4 space-y-2">
          {files.map((f) => (
            <li
              key={f.id}
              className="flex items-center gap-3 bg-white border border-gray-200
                         rounded-xl px-4 py-3 hover:border-gray-300 transition"
            >
              <span className="text-xl shrink-0">{fileIcon(f.content_type)}</span>

              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">
                  {f.original_name}
                </p>
                <p className="text-xs text-gray-400">
                  {fmtSize(f.size_bytes)} · {fmtDate(f.uploaded_at)}
                </p>
              </div>

              <div className="flex gap-2 shrink-0">
                <button
                  onClick={() => handleDownload(f.id, f.original_name)}
                  className="text-xs font-medium text-indigo-600 hover:text-indigo-800
                             border border-indigo-200 hover:bg-indigo-50
                             px-2.5 py-1 rounded-lg transition"
                >
                  Скачать
                </button>
                <button
                  onClick={() => handleDelete(f.id, f.original_name)}
                  className="text-xs font-medium text-red-500 hover:text-red-700
                             border border-red-200 hover:bg-red-50
                             px-2.5 py-1 rounded-lg transition"
                >
                  Удалить
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
