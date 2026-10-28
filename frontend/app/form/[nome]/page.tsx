"use client"; 

import { useParams } from "next/navigation";
import React, { useContext, useEffect, useState } from "react";
import { Header } from "../../_components/header";
import formsServices from "../../services/ContactsService";
import { Button } from "@/app/_components/ui/button";
import { useRouter } from "next/navigation";
import { BackArrow } from "@/app/_components/BackArrow";
import Loader from "@/app/_components/loader";
import { Formik, Field, Form, ErrorMessage } from 'formik';
import * as Yup from 'yup';

const columns = [
  { head: "Aluno", accessor: "student_name" },
  { head: "Data de Nascimento", accessor: "student_birth_date" },
  { head: "Série", accessor: "student_grade_year" },
  { head: "Turma", accessor: "student_class_name" },
  { head: "Data da Solicitação", accessor: "created_at" },
  { head: "Status", accessor: "status" },
];

export default function Solicitações() {
  const router = useParams();
  const rota = useRouter()
  const [user, setUser] = useState(null);
 
  const [data, setData] = useState<any[]>([]);
  const [parent, setParent] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [formStaffError, setFormStaffError] = useState(false)
  const [showAnswers, setShowAnswers] = useState(true)
  const [staffAnswers, setstaffAnswers] = useState<any[]>()
  const [closeStaffFields, setCloseStaffFields] = useState(false)
  const [statusFormFinished, setStatusFormFinished] = useState(false)

  const { nome: id } = router

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
    status: Yup.string()
    .required('Selecione um status')
  });

  const handleFinalize = async (status : any) => {
    const formUpdateStatus = await formsServices.updateFormStatus(id, status)
    if (!formUpdateStatus) {
      console.log(formUpdateStatus)
      return false
    }
    return true
  }

  const handleStaffForm = async (values : any) => {
    try {
      const formStaffSubmited = await formsServices.createFormStaff({values, data, user})
      const formStatus = await handleFinalize(values.status)

      setShowAnswers(true)
      setCloseStaffFields(true)

      if (!formStatus) {
        console.log('erro status')
        return null
      }

      if (!formStaffSubmited) {
        setFormStaffError(true)
        console.log('error', formStaffSubmited)
      }
    } catch (error) {
      setFormStaffError(true)
      console.error('Erro no envio do formulário:', error)
    }
  }


  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await formsServices.listFormsByUser();
        const aplication = await formsServices.listAplications();
        const staffForm = await formsServices.listStaffForms();
        const responseData = await formsServices.listUser();
  

        const filteredApplications = aplication.filter((item: any) =>
          Array.isArray(item.groups) && item.groups.length === 1 && item.groups[0] === 2
        );
  
        setUser(responseData); 

  
        if (filteredApplications.length > 0) {
          setParent(false);
        } else {
          setParent(true);
        }
  
        const matchingForms = staffForm.filter((item: any) => item.parent_form_id == id);
        if (matchingForms.length > 0) {
          setstaffAnswers(matchingForms); 
          setStatusFormFinished(true); 
        }
  
        const responseFiltered = response.filter((ele: any) => ele.id == id);
        setData(responseFiltered); 
  
      } catch (error) {
        console.error('ERROR:', error);
        setData([]); 
      } finally {
        setIsLoading(false); 
      }
    };
  
    fetchData(); 
  }, [id]); 

  useEffect(() => {

  }, [user]); 
  

  return (
    <>
     {isLoading ? <Loader isLoading={isLoading}/> : 
      <>
        <Header />
        <div className="max-w-2xl px-5 pt-5 bg-card min-h-[480px] mt-[72px] mx-auto rounded-[20px] shadow-[0_10px_60px_0_rgba(226,236,249,0.5)]">
          <Button onClick={() => rota.back()}><BackArrow /></Button>
          <h2 className="text-xl font-bold">Solicitações</h2>
          <br/>
          { data.map(element => (
            <React.Fragment key={element.id}>
              <div className="max-w-2xl mx-auto p-6 bg-card rounded-lg ">
                {/* Informações do Aluno */}
                <header className="mb-6">
                  <p className="text-2xl font-bold text-foreground mb-8">
                    Nome do Aluno: {element?.student_name || 'Aluno não encontrado'}
                  </p>

                  <p className="text-2xl font-bold text-foreground">Nome do Responsável: {element?.responsible_party?.first_name || 'Responsável não encontrado'} </p>
                  
                </header>

                {/* Série e Turma */}
                <section aria-labelledby="student-info" className="mb-6">
                  <h2 id="student-info" className="sr-only">Informações do Aluno</h2>
                  <dl className="text-muted-foreground">
                    <div className="flex items-center mb-2">
                      <dt className="font-semibold w-24">Série:</dt>
                      <dd className="text-lg">{element?.student_grade_year}ª Série</dd>
                    </div>
                    <div className="flex items-center">
                      <dt className="font-semibold w-24">Turma:</dt>
                      <dd className="text-lg">{element?.student_class_name}</dd>
                    </div>
                  </dl>
                </section>

                {/* Descrição do Problema */}
                <section aria-labelledby="issue-description" className="bg-muted p-4 rounded-lg mb-6">
                  <h2 id="issue-description" className="text-lg font-semibold text-foreground mb-2">
                    Descrição do Problema
                  </h2>
                  <p className="text-brand-text">
                    {element?.issue_description || 'Nenhuma descrição disponível.'}
                  </p>
                </section>

                {showAnswers ? 
                    <>
                      <section aria-labelledby="staff-answer-1" className="bg-card p-6 rounded-lg shadow-md mb-6 border-l-4 border-primary">
                        <h2 id="staff-answer-1" className="text-xl font-semibold text-foreground mb-3">
                          Descrição do Problema
                        </h2>
                        <p className="text-brand-text text-lg">
                          {staffAnswers && staffAnswers?.length > 0 ? staffAnswers[0]?.school_advice : 'Nenhuma descrição disponível.'}
                        </p>
                      </section>

                      <section aria-labelledby="staff-answer-2" className="bg-card p-6 rounded-lg shadow-md mb-6 border-l-4 border-secondary">
                        <h2 id="staff-answer-2" className="text-xl font-semibold text-foreground mb-3">
                          Ações Tomadas
                        </h2>
                        <p className="text-brand-text text-lg">
                          {staffAnswers && staffAnswers?.length > 0 ? staffAnswers[0]?.actions_taken : 'Nenhuma ação tomada até o momento.'}
                        </p>
                      </section>

                      <section aria-labelledby="staff-answer-3" className="bg-card p-6 rounded-lg shadow-md mb-6 border-l-4 border-accent">
                        <h2 id="staff-answer-3" className="text-xl font-semibold text-foreground mb-3">
                          Notas Finais
                        </h2>
                        <p className="text-brand-text text-lg">
                          {staffAnswers && staffAnswers?.length > 0 ? staffAnswers[0]?.final_notes : 'Nenhuma nota final disponível.'}
                        </p>
                      </section>
                    </>
                  : null }

                {/* Resposta do Colaborador */}
                {!parent && !closeStaffFields && !statusFormFinished 
                ? 
                <section aria-labelledby="collaborator-response" className="bg-muted p-4 rounded-lg">
                <Formik
                  initialValues={{
                    collaboratorResponse: '',
                    actionToTake: '',
                    measuresToTake: '',
                    status: '',
                  }}
                  validationSchema={validationSchema}
                  onSubmit={handleStaffForm}
                >
                  {({ handleChange, handleBlur, values, errors, touched, dirty, isValid }) => (
                    <Form>
                      {/* Resposta do Colaborador */}
                      <h2 id="collaborator-response" className="text-lg font-semibold text-primary mb-2">
                        Resposta do Colaborador
                      </h2>
                      <Field
                        as="textarea"
                        name="collaboratorResponse"
                        className={`w-full h-32 p-3 border ${touched.collaboratorResponse && errors.collaboratorResponse ? 'border-destructive' : 'border-primary'} rounded-lg focus:outline-none focus:border-primary`}
                        placeholder="Escreva sua resposta aqui..."
                        onChange={handleChange}
                        onBlur={handleBlur}
                        value={values.collaboratorResponse}
                      />
                      <ErrorMessage
                        name="collaboratorResponse"
                        component="div"
                        className="text-destructive text-sm mt-1"
                      />
              
                      {/* O que fazer */}
                      <h2 id="what-to-do" className="text-lg font-semibold text-primary mb-2">
                        O que fazer
                      </h2>
                      <Field
                        as="textarea"
                        name="actionToTake"
                        className={`w-full h-32 p-3 border ${touched.actionToTake && errors.actionToTake ? 'border-destructive' : 'border-primary'} rounded-lg focus:outline-none focus:border-primary`}
                        placeholder="Escreva sua resposta aqui..."
                        onChange={handleChange}
                        onBlur={handleBlur}
                        value={values.actionToTake}
                      />
                      <ErrorMessage
                        name="actionToTake"
                        component="div"
                        className="text-destructive text-sm mt-1"
                      />
              
                      {/* Medidas a tomar */}
                      <h2 id="measures-to-take" className="text-lg font-semibold text-primary mb-2">
                        Medidas a tomar
                      </h2>
                      <Field
                        as="textarea"
                        name="measuresToTake"
                        className={`w-full h-32 p-3 border ${touched.measuresToTake && errors.measuresToTake ? 'border-destructive' : 'border-primary'} rounded-lg focus:outline-none focus:border-primary`}
                        placeholder="Escreva sua resposta aqui..."
                        onChange={handleChange}
                        onBlur={handleBlur}
                        value={values.measuresToTake}
                      />
                      <ErrorMessage
                        name="measuresToTake"
                        component="div"
                        className="text-destructive text-sm mt-1"
                      />
              
                      {/* Status */}
                      <div className="flex flex-col items-end mb-2">
                        <Field 
                          as="select" 
                          name="status" 
                          className="mt-3 px-4 py-2 border-input border rounded-md bg-muted text-brand-text focus:outline-none focus:ring-2 focus:ring-ring"
                        >
                          <option value="" disabled className="text-muted-foreground">Selecione um status</option>
                          <option value="0">Pendente</option>
                          <option value="2">Finalizado</option>
                          <option value="3">Cancelado</option>
                          <option value="1">Em andamento</option>
                        </Field>
                        <ErrorMessage
                          name="status"
                          component="div"
                          className="text-destructive text-sm mt-1"
                        />
                      </div>
              
                      {/* Botão de Submissão */}
                      <div className="flex justify-between mt-4">
                        <button
                          type="submit"
                          className={`px-4 py-2 rounded-lg text-white ${
                            !(isValid && dirty)
                              ? 'bg-muted-foreground cursor-not-allowed'
                              : 'bg-primary hover:bg-primary/90'
                          }`}
                          disabled={!(isValid && dirty)} 
                        >
                          Enviar Resposta
                        </button>
                      </div>
              
                      {/* Mensagem de erro */}
                      {formStaffError && (
                        <h1 className="text-destructive text-sm mt-4">
                          JÁ EXISTE UM COLABORADOR LIDANDO COM ESTE FORMULÁRIO
                        </h1>
                      )}
                    </Form>
                  )}
                </Formik>
              </section>
              
                : null}
              </div>
            </React.Fragment>
          ))}
        </div>
      </>
     }
    </> 
  );
}
