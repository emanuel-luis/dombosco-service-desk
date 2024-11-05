"use client"; 
import React, { useEffect, useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Button } from "../_components/ui/button";
import useLoginValidation from "../utils/loginValidation"
import Loader from "../_components/loader";
import * as Yup from "yup"


const AlunoForm = ({toggleChange, formValues} : any) => {
  useLoginValidation()

  const [isDisable, setIsDisable] = useState(false)
  const [formInfo, setFormInfo] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  const validationSchema = Yup.object({
  
    nomeAluno: Yup.string()
    .required('Campo nome é obrigatório'),
    dataNascimento: Yup.date()
    .max(new Date(), "Data de nascimento deve ser no passado")
    .nullable(),
    serie: Yup.string()
    .min(1, "Ano/Série é obrigatório"),
    turma: Yup.string()
    .min(1, "Turma é obrigatória"),
  });
  
  const initialValues = {
    nomeAluno: "",
    dataNascimento: "",
    serie: "",
    dataAtendimento: "",
    turma: "",
  };

  const handleSubmit = (itens : any) => {
    try {
      toggleChange(
        Object.assign({}, itens.values, formValues)
      );
    } catch(error) {
      console.log(error)
    } finally {
      setIsLoading(false)
    }

  };

  return (
    <>
  
    <div className="flex justify-center items-center">
      <div className="w-full max-w-md px-5 pt-5">

        <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={handleSubmit}>
          {({ values, errors, touched, dirty, isValid} : any) => (
            <Form>
              <div className="mb-4">
                <label htmlFor="nomeAluno" className="hidden text-sm font-medium">
                  Nome do Aluno
                </label>
                <Field
                  name="nomeAluno"
                  type="text"
                  className={`w-[389px] h-[52px] border ${
                    errors.nomeAluno && touched.nomeAluno ? 'border-red-600' : 'border-gray-300'
                  } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                  placeholder="Nome do Aluno"
                />
                <ErrorMessage
                  name="nomeAluno"
                  component="div"
                  className="text-red-600 text-sm"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="dataNascimento"
                  className="hidden text-sm font-medium"
                >
                  Data de Nascimento
                </label>
                <Field
                  name="dataNascimento"
                  type="date" // TIRA ISSO AQUI E PÕE UMA MÁSCARA
                  className={`w-[389px] h-[52px] border ${
                    errors.dataNascimento && touched.dataNascimento ? 'border-red-600' : 'border-gray-300'
                  } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                  placeholder="Data de Nascimento"
                />
                <ErrorMessage
                  name="dataNascimento"
                  component="div"
                  className="text-red-600 text-sm"
                />
              </div>

              <div className="mb-4">
                <label htmlFor="serie" className="hidden text-sm font-medium">
                  Ano/Série
                </label>
                <Field
                  name="serie"
                  type="text"
                  className={`w-[389px] h-[52px] border ${
                    errors.serie && touched.serie ? 'border-red-600' : 'border-gray-300'
                  } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                  placeholder="Ano/Série"
                />
                <ErrorMessage
                  name="serie"
                  component="div"
                  className="text-red-600 text-sm"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="dataAtendimento"
                  className="hidden text-sm font-medium"
                >
                  Data de Atendimento
                </label>
                <Field
                  name="dataAtendimento"
                  type="date"
                  className={`w-[389px] h-[52px] border ${
                    errors.dataAtendimento && touched.dataAtendimento ? 'border-red-600' : 'border-gray-300'
                  } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                  placeholder="Data de Atendimento"
                />
                <ErrorMessage
                  name="dataAtendimento"
                  component="div"
                  className="text-red-600 text-sm"
                />
              </div>

              <div className="mb-4">
                <label htmlFor="turma" className="hidden text-sm font-medium">
                  Turma
                </label>
                <Field
                  name="turma"
                  type="text"
                  className={`w-[389px] h-[52px] border ${
                    errors.turma && touched.turma ? 'border-red-600' : 'border-gray-300'
                  } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                  placeholder="Turma"
                />
                <ErrorMessage
                  name="turma"
                  component="div"
                  className="text-red-600 text-sm"
                />
              </div>

              <Button
                type="button"
                className={`${isDisable ? "bg-[#BCBCBC]" : "bg-[#5061FC]"} w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] mt-8 text-white`}
                onClick={() => {handleSubmit(values)}}
                disabled={!(isValid && dirty)}
              >
                Enviar
              </Button>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  </>
  );
};

export default AlunoForm;
