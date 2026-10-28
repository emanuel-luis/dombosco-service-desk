"use client";

import React, { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";
import { toMessage } from "../lib/errors";
import { canEditComment } from "../lib/roles";
import { Comment, FormStatus, STATUS, UserInfo } from "../lib/types";

interface CommentsProps {
  formId: number;
  status: FormStatus;
  user: UserInfo | null;
}

const fieldClass =
  "w-full h-24 p-3 border border-input rounded-lg focus:outline-none focus:border-primary";

export default function Comments({ formId, status, user }: CommentsProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [text, setText] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [error, setError] = useState("");

  // The API rejects comments on pending requests (409), so there is nothing to load.
  const enabled = status !== STATUS.PENDENTE;

  const load = useCallback(async () => {
    try {
      setComments(await api.listComments(formId));
    } catch (e) {
      setError(toMessage(e));
    }
  }, [formId]);

  useEffect(() => {
    if (enabled) load();
  }, [enabled, load]);

  // Runs an API call, then reloads the thread; failures are shown inline.
  const run = async (action: () => Promise<unknown>, onDone?: () => void) => {
    setError("");
    try {
      await action();
      onDone?.();
      await load();
    } catch (e) {
      setError(toMessage(e));
    }
  };

  return (
    <section aria-labelledby="comments" className="bg-muted p-4 rounded-lg mt-6">
      <h2 id="comments" className="text-lg font-semibold text-primary mb-2">
        Comentários
      </h2>

      {!enabled ? (
        <p className="text-brand-text">
          Os comentários ficam disponíveis depois que a solicitação é atendida.
        </p>
      ) : (
        <>
          {comments.length === 0 && !error && (
            <p className="text-brand-text">Nenhum comentário até o momento.</p>
          )}
          <ul className="space-y-3">
            {comments.map((c) => (
              <li key={c.id} className="bg-card p-3 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  {c.user} em {new Date(c.created_at).toLocaleString("pt-BR")}
                </p>
                {editingId === c.id ? (
                  <>
                    <textarea
                      className={fieldClass}
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                    />
                    <div className="flex gap-4 mt-2 text-sm">
                      <button
                        type="button"
                        className="text-primary underline"
                        disabled={editText.trim() === ""}
                        onClick={() =>
                          run(
                            () => api.updateComment(c.id, editText.trim()),
                            () => setEditingId(null),
                          )
                        }
                      >
                        Salvar
                      </button>
                      <button
                        type="button"
                        className="underline"
                        onClick={() => setEditingId(null)}
                      >
                        Cancelar
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <p className="text-brand-text whitespace-pre-wrap">{c.comment}</p>
                    {canEditComment(c.user_id, status, user) && (
                      <div className="flex gap-4 mt-2 text-sm">
                        <button
                          type="button"
                          className="text-primary underline"
                          onClick={() => {
                            setEditingId(c.id);
                            setEditText(c.comment);
                          }}
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          className="text-destructive underline"
                          onClick={() => {
                            if (window.confirm("Apagar este comentário?")) {
                              run(() => api.deleteComment(c.id));
                            }
                          }}
                        >
                          Apagar
                        </button>
                      </div>
                    )}
                  </>
                )}
              </li>
            ))}
          </ul>

          <label htmlFor="new-comment" className="sr-only">
            Novo comentário
          </label>
          <textarea
            id="new-comment"
            className={`${fieldClass} mt-4`}
            placeholder="Escreva um comentário..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button
            type="button"
            disabled={text.trim() === ""}
            className="mt-2 px-4 py-2 rounded-lg text-white bg-primary hover:bg-primary/90 disabled:bg-muted-foreground disabled:cursor-not-allowed"
            onClick={() =>
              run(
                () => api.createComment(formId, text.trim()),
                () => setText(""),
              )
            }
          >
            Comentar
          </button>
        </>
      )}

      {error && (
        <p role="alert" className="text-destructive text-sm mt-2">
          {error}
        </p>
      )}
    </section>
  );
}
