"use client"

import React, { useEffect, useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Button } from "../_components/ui/button";
import { Header } from "../_components/header";
import AlunoForm from "../_components/StudentForm";
import formsServices from "../services/ContactsService";
import Confirm from "../_components/Success";
import Loader from "../_components/loader";
import { useRouter } from "next/navigation";
import InputMask from 'react-input-mask';
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
  const [choices, setChoices] = useState([])
  const [parent, setParent] = useState(true)

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

  const handleSubmit = () => {
    console.log("Formulário enviado da onde não era pra enviar")
  };

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

    const relationship = {
        "0": "Pai",
        "1": "Mãe",
        "2": "Avô",
        "3": "Avó",
        "4": "Tio",
        "5": "Tia",
        "6": "Irmão",
        "7": "Irmã",
        "8": "Outro"
    };
    
    const aplication = await formsServices.listAplications();
    const filteredApplications = aplication.filter((item: any) =>
      Array.isArray(item.groups) && item.groups.length === 1 && item.groups[0] === 2
    );
    if (filteredApplications.length > 0) {
      setParent(false); 
    }
   
    function getRelationshipKey() {
        for (const [key, relValue] of Object.entries(relationship)) {
            if (relValue.toLowerCase() === parentValue?.parentesco.toLowerCase()) {  
                return key;
            }
        }
        return null; 
    }

    data = {
      "requested_by": parent ? 0 : 1, // WARNING
      "student_name": data.nomeAluno,  
      "student_birth_date": data.dataNascimento.split('/').reverse().join("-"), 
      "student_grade_year": data.serie,
      "student_class_name": data.turma,
      "relationship_to_student": getRelationshipKey(),
      "issue_description": tratativaValue?.tratativa
    }

    try {
      await formsServices.createForm(data)
      setResponseTrue(true)
    } catch(error) {
      console.log(error)
    } finally {
      setIsLoading(false)
    }
  }


  useEffect(() => {
    setIsLoading(true)

    const data = async () => {
      try {
        const choicesDate = await formsServices.listChoices()
        setChoices(choicesDate.relationship)
        setIsLoading(false)

      } catch(error) {
        console.log(error)
      } finally {
        setIsLoading(false)
      }
    }

    data()
  }
  , [])

  return  (
    <>
      <Header />
      {
      isLoading
       ? <Loader isLoading={isLoading} /> : 
       <div className="flex justify-center items-center w-full">
       <div className="w-full max-w-md px-5 pt-5">
         <button onClick={() => showTratativa && !studentForm ? handleBack() : !studentForm ? router.back() : hideStudentForm()} className="text-[#5061FC] mb-5"><img className="-rotate-90" src="/arrow.svg"/></button>
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
                           errors.nome && touched.nome ? 'border-red-600' : 'border-gray-300'
                         } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                         placeholder="Nome"
                       />
                       <ErrorMessage name="nome" component="div" className="text-red-600 text-sm mt-1" />
                     </div>

                     <div className="mb-4">
                       <label htmlFor="parentesco" className="text-sm font-medium">
                       </label>
                       <Field
                         as="select" 
                         name="parentesco"
                         className={`w-[389px] h-[52px] border ${
                           errors.parentesco && touched.parentesco ? 'border-red-600' : 'border-gray-300'
                         } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                       >
                         <option value="" label="Selecione uma opção" />
                         {Object.values(choices).map(element => {
                           return <option key={element} value={element} label={element} />
                         })}
                         
                       </Field>
                       <ErrorMessage name="parentesco" component="div" className="text-red-600 text-sm mt-1" />
                     </div>

                     <div className="mb-4">
                     <label htmlFor="phone" className="hidden text-sm font-medium">
                       Telefone
                     </label>
                     <Field name="phone">
                       {({ field } : any) => (
                         <InputMask
                           {...field}
                           mask="(99) 99999-9999" // Máscara para telefone celular
                           className={`w-[389px] h-[52px] border ${
                             errors.phone && touched.phone ? 'border-red-600' : 'border-gray-300'
                           } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                           placeholder="Telefone"
                         />
                       )}
                     </Field>
                     <ErrorMessage name="phone" component="div" className="text-red-600 text-sm mt-1" />
                   </div>

                   <Button                    
                     type="button"
                     onClick={() => handleAdvance(values)}
                     className="bg-[#5061FC] w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] mt-8 text-white"
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
