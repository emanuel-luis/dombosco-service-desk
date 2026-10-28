"use client";

import { useParams, useRouter } from "next/navigation";
import React, { useCallback, useEffect, useState } from "react";
import { Header } from "../../_components/header";
import { Button } from "@/app/_components/ui/button";
import { BackArrow } from "@/app/_components/BackArrow";
import Loader from "@/app/_components/loader";
import Comments from "@/app/_components/Comments";
import { useAuth } from "../../context/authContext";
import { api } from "../../lib/api";
import { toMessage } from "../../lib/errors";
import {
  allowedStatuses,
  canAnswer,
  canEditOrDelete,
} from "../../lib/roles";
import {
  FormStatus,
  ParentForm,
  STATUS_LABELS,
  StaffForm,
} from "../../lib/types";
import { Formik, Field, Form, ErrorMessage } from 'formik';
import * as Yup from 'yup';

const validationSchema = Yup.object({
  collaboratorResponse: Yup.string()
    .required('A resposta do colaborador é obrigatória.')
    .min(10, 'A resposta deve ter no mínimo 10 caracteres.'),
  actionToTake: Yup.string()
    .required('Informe o que fazer.')
    .min(5, 'A descrição do que fazer deve ter no mínimo 5 caracteres.'),
  measuresToTake: Yup.string()
    .required('As medidas a tomar são obrigatórias.')
    .min(5, 'A descrição das medidas deve ter no mínimo 5 caracteres.'),
});

const areaClass = (invalid: boolean) =>
  `w-full h-32 p-3 border ${invalid ? 'border-destructive' : 'border-primary'} rounded-lg focus:outline-none focus:border-primary`;

export default function Solicitações() {
  const { nome: id } = useParams<{ nome: string }>();
  const rota = useRouter();
  const { role, user, userLoading } = useAuth();

  const [form, setForm] = useState<ParentForm | null>(null);
  const [staffAnswer, setStaffAnswer] = useState<StaffForm | null>(null);
  const [assigned, setAssigned] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [description, setDescription] = useState("");
  const [nextStatus, setNextStatus] = useState("");

  const load = useCallback(async () => {
    try {
      const current = await api.getForm(id);
      const [answers, mine] = await Promise.all([
        api.listStaffForms(),
        role === "staff" && user
          ? api.listForms({ assigned_staff: user.email })
          : Promise.resolve([] as ParentForm[]),
      ]);
      setForm(current);
      setStaffAnswer(answers.find((a) => a.parent_form_id === current.id) ?? null);
      setAssigned(mine.some((f) => f.id === current.id));
      setError("");
    } catch (e) {
      setError(toMessage(e));
    } finally {
      setIsLoading(false);
    }
  }, [id, role, user]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- loads the request once the user is known
    if (!userLoading) load();
  }, [userLoading, load]);

  // Runs a change, then reloads the request; failures are shown inline.
  const run = async (action: () => Promise<unknown>) => {
    setError("");
    try {
      await action();
      await load();
      return true;
    } catch (e) {
      setError(toMessage(e));
      return false;
    }
  };

  const saveDescription = async () => {
    if (!form) return;
    const { id: _id, responsible_party, status, created_at, updated_at, ...input } = form;
    if (await run(() => api.updateForm(form.id, { ...input, issue_description: description.trim() }))) {
      setEditing(false);
    }
  };

  const changeStatus = (status: FormStatus) => form && run(() => api.updateStatus(form.id, status));

  const canChange = form ? allowedStatuses(role, form.status, assigned, staffAnswer !== null) : [];

  return (
    <>
     {isLoading || userLoading ? <Loader isLoading /> :
      <>
        <Header />
        <div className="max-w-2xl px-5 pt-5 bg-card min-h-[480px] mt-[72px] mx-auto rounded-[20px] shadow-[0_10px_60px_0_rgba(226,236,249,0.5)]">
          <Button onClick={() => rota.back()}><BackArrow /></Button>
          <h2 className="text-xl font-bold">Solicitações</h2>
          <br/>
          {error && (
            <p role="alert" className="text-destructive text-sm mb-4">{error}</p>
          )}
          { form && (
              <div className="max-w-2xl mx-auto p-6 bg-card rounded-lg ">
                {/* Informações do Aluno */}
                <header className="mb-6">
                  <p className="text-2xl font-bold text-foreground mb-8">
                    Nome do Aluno: {form.student_name}
                  </p>

                  <p className="text-2xl font-bold text-foreground">Nome do Responsável: {form.responsible_party?.first_name} </p>
                  <p className="mt-2 text-muted-foreground">Status: {STATUS_LABELS[form.status]}</p>
                </header>

                {/* Série e Turma */}
                <section aria-labelledby="student-info" className="mb-6">
                  <h2 id="student-info" className="sr-only">Informações do Aluno</h2>
                  <dl className="text-muted-foreground">
                    <div className="flex items-center mb-2">
                      <dt className="font-semibold w-24">Série:</dt>
                      <dd className="text-lg">{form.student_grade_year}ª Série</dd>
                    </div>
                    <div className="flex items-center">
                      <dt className="font-semibold w-24">Turma:</dt>
                      <dd className="text-lg">{form.student_class_name}</dd>
                    </div>
                  </dl>
                </section>

                {/* Descrição do Problema */}
                <section aria-labelledby="issue-description" className="bg-muted p-4 rounded-lg mb-6">
                  <h2 id="issue-description" className="text-lg font-semibold text-foreground mb-2">
                    Descrição do Problema
                  </h2>
                  {editing ? (
                    <>
                      <textarea
                        className={areaClass(description.trim() === "")}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                      />
                      <div className="flex gap-4 mt-2 text-sm">
                        <button
                          type="button"
                          className="text-primary underline"
                          disabled={description.trim() === ""}
                          onClick={saveDescription}
                        >
                          Salvar
                        </button>
                        <button type="button" className="underline" onClick={() => setEditing(false)}>
                          Cancelar
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <p className="text-brand-text">
                        {form.issue_description || 'Nenhuma descrição disponível.'}
                      </p>
                      {canEditOrDelete(role, form, user) && (
                        <button
                          type="button"
                          className="mt-2 text-sm text-primary underline"
                          onClick={() => {
                            setDescription(form.issue_description);
                            setEditing(true);
                          }}
                        >
                          Editar descrição
                        </button>
                      )}
                    </>
                  )}
                </section>

                {staffAnswer && (
                  <>
                    <section aria-labelledby="staff-answer-1" className="bg-card p-6 rounded-lg shadow-md mb-6 border-l-4 border-primary">
                      <h2 id="staff-answer-1" className="text-xl font-semibold text-foreground mb-3">
                        Resposta da Escola
                      </h2>
                      <p className="text-brand-text text-lg">
                        {staffAnswer.school_advice || 'Nenhuma resposta disponível.'}
                      </p>
                    </section>

                    <section aria-labelledby="staff-answer-2" className="bg-card p-6 rounded-lg shadow-md mb-6 border-l-4 border-secondary">
                      <h2 id="staff-answer-2" className="text-xl font-semibold text-foreground mb-3">
                        Ações Tomadas
                      </h2>
                      <p className="text-brand-text text-lg">
                        {staffAnswer.actions_taken || 'Nenhuma ação tomada até o momento.'}
                      </p>
                    </section>

                    <section aria-labelledby="staff-answer-3" className="bg-card p-6 rounded-lg shadow-md mb-6 border-l-4 border-primary">
                      <h2 id="staff-answer-3" className="text-xl font-semibold text-foreground mb-3">
                        Notas Finais
                      </h2>
                      <p className="text-brand-text text-lg">
                        {staffAnswer.final_notes || 'Nenhuma nota final disponível.'}
                      </p>
                    </section>
                  </>
                )}

                {/* Mudança de status: equipe atribuída ou administrador */}
                {canChange.length > 0 && (
                  <section aria-labelledby="status-change" className="bg-muted p-4 rounded-lg mb-6">
                    <h2 id="status-change" className="text-lg font-semibold text-primary mb-2">
                      Alterar status
                    </h2>
                    <div className="flex gap-3 items-center">
                      <select
                        value={nextStatus}
                        onChange={(e) => setNextStatus(e.target.value)}
                        aria-label="Novo status"
                        className="px-4 py-2 border-input border rounded-md bg-card text-brand-text focus:outline-none focus:ring-2 focus:ring-ring"
                      >
                        <option value="" disabled>Selecione um status</option>
                        {canChange.map((s) => (
                          <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                        ))}
                      </select>
                      <button
                        type="button"
                        disabled={nextStatus === ""}
                        onClick={async () => {
                          if (await changeStatus(Number(nextStatus) as FormStatus)) setNextStatus("");
                        }}
                        className="px-4 py-2 rounded-lg text-white bg-primary hover:bg-primary/90 disabled:bg-muted-foreground disabled:cursor-not-allowed"
                      >
                        Alterar
                      </button>
                    </div>
                  </section>
                )}

                {/* Resposta do Colaborador: só a equipe, e só para solicitações pendentes */}
                {canAnswer(role, form) && (
                  <section aria-labelledby="collaborator-response" className="bg-muted p-4 rounded-lg">
                    <Formik
                      initialValues={{
                        collaboratorResponse: '',
                        actionToTake: '',
                        measuresToTake: '',
                      }}
                      validationSchema={validationSchema}
                      onSubmit={async (values) => {
                        await run(() =>
                          api.createStaffForm({
                            parent_form_id: form.id,
                            school_advice: values.collaboratorResponse,
                            actions_taken: values.actionToTake,
                            final_notes: values.measuresToTake,
                          }),
                        );
                      }}
                    >
                      {({ errors, touched, dirty, isValid, isSubmitting }) => (
                        <Form>
                          <h2 id="collaborator-response" className="text-lg font-semibold text-primary mb-2">
                            Resposta do Colaborador
                          </h2>
                          <Field
                            as="textarea"
                            name="collaboratorResponse"
                            className={areaClass(!!(touched.collaboratorResponse && errors.collaboratorResponse))}
                            placeholder="Escreva sua resposta aqui..."
                          />
                          <ErrorMessage name="collaboratorResponse" component="div" className="text-destructive text-sm mt-1" />

                          <h2 id="what-to-do" className="text-lg font-semibold text-primary mb-2">
                            O que fazer
                          </h2>
                          <Field
                            as="textarea"
                            name="actionToTake"
                            className={areaClass(!!(touched.actionToTake && errors.actionToTake))}
                            placeholder="Escreva sua resposta aqui..."
                          />
                          <ErrorMessage name="actionToTake" component="div" className="text-destructive text-sm mt-1" />

                          <h2 id="measures-to-take" className="text-lg font-semibold text-primary mb-2">
                            Medidas a tomar
                          </h2>
                          <Field
                            as="textarea"
                            name="measuresToTake"
                            className={areaClass(!!(touched.measuresToTake && errors.measuresToTake))}
                            placeholder="Escreva sua resposta aqui..."
                          />
                          <ErrorMessage name="measuresToTake" component="div" className="text-destructive text-sm mt-1" />

                          <div className="flex justify-between mt-4">
                            <button
                              type="submit"
                              className={`px-4 py-2 rounded-lg text-white ${
                                !(isValid && dirty) || isSubmitting
                                  ? 'bg-muted-foreground cursor-not-allowed'
                                  : 'bg-primary hover:bg-primary/90'
                              }`}
                              disabled={!(isValid && dirty) || isSubmitting}
                            >
                              Enviar Resposta
                            </button>
                          </div>
                        </Form>
                      )}
                    </Formik>
                  </section>
                )}

                <Comments formId={form.id} status={form.status} user={user} />
              </div>
          )}
        </div>
      </>
     }
    </>
  );
}
