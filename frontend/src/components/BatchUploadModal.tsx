/**
 * BatchUploadModal — carrega recebíveis em lote a partir de um arquivo CSV.
 *
 * Formato esperado do CSV (com cabeçalho):
 *   assignor_document,product_code,face_value,currency,issue_date,due_date,external_reference
 *
 * Exemplo:
 *   36160198000118,DUPLICATA_MERCANTIL,15000.00,BRL,2026-05-19,2026-08-19,NF-2001
 */

import { type DragEvent, useRef, useState } from 'react';

import { ApiClientError } from '../api/client';
import { createReceivable } from '../api/endpoints';
import type { ReceivableCreate } from '../types/domain';

interface Props {
  onClose: () => void;
  onDone: (created: number, errors: number) => void;
}

interface CsvRow {
  assignor_document: string;
  product_code: string;
  face_value: string;
  currency: string;
  issue_date: string;
  due_date: string;
  external_reference: string;
}

interface RowResult {
  ref: string;
  status: 'ok' | 'error';
  message: string;
}

const REQUIRED_HEADERS: (keyof CsvRow)[] = [
  'assignor_document',
  'product_code',
  'face_value',
  'currency',
  'issue_date',
  'due_date',
  'external_reference',
];

function parseCsv(text: string): CsvRow[] {
  const lines = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
  const header = lines[0]?.split(',').map((h) => h.trim().toLowerCase());
  if (!header) throw new Error('Arquivo CSV vazio.');

  const missing = REQUIRED_HEADERS.filter((h) => !header.includes(h));
  if (missing.length) throw new Error(`Colunas ausentes: ${missing.join(', ')}`);

  return lines
    .slice(1)
    .filter((l) => l.trim())
    .map((line) => {
      const vals = line.split(',').map((v) => v.trim());
      return Object.fromEntries(
        REQUIRED_HEADERS.map((key) => [key, vals[header.indexOf(key)] ?? '']),
      ) as CsvRow;
    });
}

function rowToPayload(row: CsvRow): ReceivableCreate {
  return {
    assignor_document: row.assignor_document.replace(/\D/g, ''),
    product_code: row.product_code.toUpperCase(),
    face_value: { amount: row.face_value, currency: row.currency.toUpperCase() },
    issue_date: row.issue_date,
    due_date: row.due_date,
    external_reference: row.external_reference,
  };
}

export function BatchUploadModal({ onClose, onDone }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [rows, setRows] = useState<CsvRow[]>([]);
  const [parseError, setParseError] = useState<string | null>(null);
  const [results, setResults] = useState<RowResult[]>([]);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const loadFile = (file: File) => {
    setParseError(null);
    setRows([]);
    setResults([]);
    setProgress(0);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = parseCsv(e.target?.result as string);
        if (parsed.length === 0) throw new Error('Nenhuma linha de dados encontrada no arquivo.');
        setRows(parsed);
      } catch (err) {
        setParseError(err instanceof Error ? err.message : String(err));
      }
    };
    reader.readAsText(file, 'utf-8');
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) loadFile(file);
  };

  const handleFileChange = () => {
    const file = fileRef.current?.files?.[0];
    if (file) loadFile(file);
  };

  const handleImport = async () => {
    setRunning(true);
    setResults([]);
    const newResults: RowResult[] = [];

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      try {
        await createReceivable(rowToPayload(row));
        newResults.push({ ref: row.external_reference, status: 'ok', message: 'Criado' });
      } catch (err) {
        const msg =
          err instanceof ApiClientError
            ? `${err.code}: ${err.message}`
            : err instanceof Error
              ? err.message
              : 'Erro desconhecido';
        newResults.push({ ref: row.external_reference, status: 'error', message: msg });
      }
      setProgress(i + 1);
      setResults([...newResults]);
    }

    setRunning(false);
    const ok = newResults.filter((r) => r.status === 'ok').length;
    const errors = newResults.filter((r) => r.status === 'error').length;
    onDone(ok, errors);
  };

  const done = results.length === rows.length && rows.length > 0 && !running;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-2xl rounded-xl bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4">
          <h2 className="text-base font-semibold text-zinc-900">Carga em lote (CSV)</h2>
          <button
            onClick={onClose}
            type="button"
            className="text-zinc-400 hover:text-zinc-700"
            aria-label="Fechar"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4 px-6 py-5">
          {/* Drop zone */}
          {rows.length === 0 && (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileRef.current?.click()}
              className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-6 py-10 text-sm transition-colors ${
                isDragging
                  ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                  : 'border-zinc-300 bg-zinc-50 text-zinc-500 hover:border-zinc-400'
              }`}
            >
              <span className="text-2xl">📂</span>
              <span>Arraste um arquivo CSV ou clique para selecionar</span>
              <span className="text-xs text-zinc-400">
                Colunas: assignor_document, product_code, face_value, currency, issue_date,
                due_date, external_reference
              </span>
              <input
                ref={fileRef}
                type="file"
                accept=".csv,text/csv"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
          )}

          {parseError && (
            <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700 ring-1 ring-inset ring-rose-200">
              {parseError}
            </p>
          )}

          {/* Preview */}
          {rows.length > 0 && results.length === 0 && !running && (
            <div>
              <p className="mb-2 text-sm text-zinc-600">
                <strong>{rows.length}</strong> recebíveis encontrados. Prévia:
              </p>
              <div className="max-h-48 overflow-y-auto rounded-md border border-zinc-200 text-xs">
                <table className="w-full">
                  <thead className="bg-zinc-50 text-zinc-500">
                    <tr>
                      <th className="px-2 py-1 text-left">Referência</th>
                      <th className="px-2 py-1 text-left">Produto</th>
                      <th className="px-2 py-1 text-right">Valor</th>
                      <th className="px-2 py-1 text-left">Moeda</th>
                      <th className="px-2 py-1 text-left">Vencimento</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r, i) => (
                      <tr key={i} className="border-t border-zinc-100">
                        <td className="px-2 py-1">{r.external_reference}</td>
                        <td className="px-2 py-1">{r.product_code}</td>
                        <td className="px-2 py-1 text-right">{r.face_value}</td>
                        <td className="px-2 py-1">{r.currency}</td>
                        <td className="px-2 py-1">{r.due_date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Progress bar */}
          {(running || (results.length > 0 && !done)) && (
            <div>
              <div className="mb-1 flex justify-between text-xs text-zinc-500">
                <span>Importando…</span>
                <span>
                  {progress}/{rows.length}
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-zinc-200">
                <div
                  className="h-2 rounded-full bg-emerald-500 transition-all"
                  style={{ width: `${(progress / rows.length) * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* Results */}
          {results.length > 0 && (
            <div className="max-h-48 overflow-y-auto rounded-md border border-zinc-200 text-xs">
              <table className="w-full">
                <thead className="bg-zinc-50 text-zinc-500">
                  <tr>
                    <th className="px-2 py-1 text-left">Referência</th>
                    <th className="px-2 py-1 text-left">Status</th>
                    <th className="px-2 py-1 text-left">Mensagem</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, i) => (
                    <tr key={i} className="border-t border-zinc-100">
                      <td className="px-2 py-1">{r.ref}</td>
                      <td className="px-2 py-1">
                        {r.status === 'ok' ? (
                          <span className="text-emerald-600">✅ OK</span>
                        ) : (
                          <span className="text-rose-600">❌ Erro</span>
                        )}
                      </td>
                      <td className="px-2 py-1 text-zinc-500">{r.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {done && (
            <p className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-700 ring-1 ring-inset ring-emerald-200">
              Importação concluída:{' '}
              <strong>{results.filter((r) => r.status === 'ok').length} criados</strong>,{' '}
              <strong className="text-rose-600">
                {results.filter((r) => r.status === 'error').length} erros
              </strong>
              .
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 border-t border-zinc-200 px-6 py-4">
          {!done && (
            <button
              type="button"
              onClick={onClose}
              className="rounded-md px-4 py-2 text-sm text-zinc-600 hover:bg-zinc-100"
            >
              Cancelar
            </button>
          )}
          {rows.length > 0 && !running && !done && (
            <button
              type="button"
              onClick={() => void handleImport()}
              className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
            >
              Importar {rows.length} recebíveis
            </button>
          )}
          {done && (
            <button
              type="button"
              onClick={onClose}
              className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
            >
              Fechar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
