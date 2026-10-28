"use client"

import React, { useEffect, useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Button } from "../_components/ui/button";
import { Header } from "../_components/header";
import AlunoForm from "../_components/StudentForm";
import { api } from "../lib/api";
import { toMessage } from "../lib/errors";
import { toIsoDate } from "../lib/birthDate";
import { canCreateRequest } from "../lib/roles";
import { useAuth } from "../context/authContext";
import Confirm from "../_components/Success";
import Loader from "../_components/loader";
import { useRouter } from "next/navigation";
import { BackArrow } from "@/app/_components/BackArrow";
import { MaskedInput } from "../_components/MaskedInput";
import * as Yup from 'yup';
import Treatment from "../_components/Treatment";
import useLoginValidation from "../utils/loginValidation"


const PersonsResponsibleForm =  () => {
  useLoginValidation()

  const [responseTrue, setResponseTrue] = useState(false);
  const [showTratativa, setShowTratativa] = useState(false);
  const [studentForm, setStudentForm] = useState(false);
  const [tratativaValue, setTratativaValue] = useState<{ tratativa?: string }>()
  const [parentValue, setParentValue] = useState<{ parentesco: string }>()
  const [isLoading, setIsLoading] = useState(true)
  const [choices, setChoices] = useState<Record<string, string>>({})
  const [error, setError] = useState("")
  const { role, userLoading } = useAuth()

  const router = useRouter()

  const initialValues = {
    nome: "",
    solicitado: "",
    parentesco: "",
    email: "",
    phone: "",
    tratativa: "",
  };

  const validationSchema = Yup.object({
    nome: Yup.string()
      .required('O campo Nome é obrigatório')
      .min(3, 'O nome deve ter pelo menos 3 caracteres')
      .max(50, 'O nome deve ter no máximo 50 caracteres'),
    parentesco: Yup.string()
      .required('O campo parentesco é obrigatório'),
    phone: Yup.string()
    .required('O campo telefone é obrigatório')
    .min(11, 'Informe o número de celular e o DDD')
    .max(15)
    .transform((value) => value.replace(/[^\d]/g, "")), 
  
  });

  // The wizard submits through its own buttons; Enter must not submit the outer form.
  const handleSubmit = () => {};

  const handleAdvance = (values : any) => {
    setParentValue(values)
    setShowTratativa(true);
  };

  const handleBack = () => {
    setShowTratativa(false);
  };

  const showStudentForm = (values : any) => {
    setTratativaValue(values)
    setStudentForm(true)
  }

  const hideStudentForm = () => {
    setStudentForm(false)
  }

  const toggleChange = async (data : any) => {
    setIsLoading(true)
    setError("")

    try {
      await api.createForm({
        requested_by: 0, // 0 = requested by the parents
        student_name: data.nomeAluno,
        student_birth_date: toIsoDate(data.dataNascimento),
        student_grade_year: Number(data.serie),
        student_class_name: data.turma,
        relationship_to_student: Number(parentValue?.parentesco),
        issue_description: tratativaValue?.tratativa ?? "",
      })
      setResponseTrue(true)
    } catch(e) {
      setError(toMessage(e))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    api
      .getChoices()
      .then((result) => setChoices(result.relationship))
      .catch((e) => setError(toMessage(e)))
      .finally(() => setIsLoading(false))
  }, [])

  return  (
    <>
      <Header />
      {
      isLoading || userLoading
       ? <Loader isLoading /> : !canCreateRequest(role)
       ? <p role="alert" className="p-8 text-center text-destructive">Apenas pais e responsáveis podem criar solicitações.</p> : 
       <div className="flex justify-center items-center w-full">
       <div className="w-full max-w-md px-5 pt-5">
         <button onClick={() => showTratativa && !studentForm ? handleBack() : !studentForm ? router.back() : hideStudentForm()} className="text-primary mb-5"><BackArrow /></button>
         {error && <p role="alert" className="text-destructive text-sm mb-4">{error}</p>}
         <h2 className="text-xl font-bold text-left mb-8">
           {!studentForm ? "Formulário de Responsável" : "Formulário do Aluno"}
         </h2>

           <Formik initialValues={initialValues} validationSchema={validationSchema}  onSubmit={handleSubmit}>
             {({ values, errors, touched, dirty, isValid}) => ( 
               <Form> 
                 {!showTratativa ? (
                   <>
                     <div className="mb-4">
                       <label htmlFor="nome" className="hidden text-sm font-medium">
                         Nome
                       </label>
                       <Field
                         name="nome"
                         type="text"
                         className={`w-[389px] h-[52px] border ${
                           errors.nome && touched.nome ? 'border-destructive' : 'border-input'
                         } rounded-[4px] p-3 bg-card shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-primary outline-none`}
                         placeholder="Nome"
                       />
                       <ErrorMessage name="nome" component="div" className="text-destructive text-sm mt-1" />
                     </div>

                     <div className="mb-4">
                       <label htmlFor="parentesco" className="text-sm font-medium">
                       </label>
                       <Field
                         as="select" 
                         name="parentesco"
                         className={`w-[389px] h-[52px] border ${
                           errors.parentesco && touched.parentesco ? 'border-destructive' : 'border-input'
                         } rounded-[4px] p-3 bg-card shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-primary outline-none`}
                       >
                         <option value="" label="Selecione uma opção" />
                         {Object.entries(choices).map(([value, label]) => (
                           <option key={value} value={value} label={label} />
                         ))}
                         
                       </Field>
                       <ErrorMessage name="parentesco" component="div" className="text-destructive text-sm mt-1" />
                     </div>

                     <div className="mb-4">
                     <label htmlFor="phone" className="hidden text-sm font-medium">
                       Telefone
                     </label>
                     <Field name="phone">
                       {({ field } : any) => (
                         <MaskedInput
                           id="phone"
                           {...field}
                           mask="(99) 99999-9999" // Máscara para telefone celular
                           className={`w-[389px] h-[52px] border ${
                             errors.phone && touched.phone ? 'border-destructive' : 'border-input'
                           } rounded-[4px] p-3 bg-card shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-primary outline-none`}
                           placeholder="Telefone"
                         />
                       )}
                     </Field>
                     <ErrorMessage name="phone" component="div" className="text-destructive text-sm mt-1" />
                   </div>

                   <Button                    
                     type="button"
                     onClick={() => handleAdvance(values)}
                     className="bg-primary w-[389px] h-[52px] border border-input rounded-[4px] p-3 shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] mt-8 text-white"
                     disabled={!(isValid && dirty)}
                   >
                     Avançar
                   </Button>
                 </>
               ) : !studentForm 
               ? ( <Treatment handleUserSubmit={showStudentForm} handleBack={handleBack}/>
               ) : responseTrue 
               ? <Confirm /> : isLoading 
               ? <Loader isLoading /> : <AlunoForm 
                       toggleChange={toggleChange}
                       formValues={values}
                   /> }
             </Form>
           )}

         </Formik>
       </div>
     </div>
    
    }
    </>
  );
};

export default PersonsResponsibleForm;
