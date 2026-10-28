"use client"; 
import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Button } from "../_components/ui/button";
import useLoginValidation from "../utils/loginValidation"
import InputMask from 'react-input-mask'
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
        .transform((value, originalValue) => {
            const isValidDate = /^\d{2}\/\d{2}\/\d{4}$/.test(originalValue);
            return isValidDate ? new Date(originalValue.split('/').reverse().join('-')) : null;
        })
        .nullable()
        .required("Data de nascimento é obrigatória")
        .test("min-age", "O aluno deve ter pelo menos 18 anos", function(value) {
            if (!value) return false;
            const today = new Date();
            const birthDate = new Date(value);
            const age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            const dayDiff = today.getDate() - birthDate.getDate();

            return age > 18 || (age === 18 && (monthDiff > 0 || (monthDiff === 0 && dayDiff >= 0)));
        }),
    serie: Yup.number()
        .min(1, "Ano/Série é obrigatório")
        .required("Ano/Série é obrigatório"),
    turma: Yup.string()
        .min(1, "Turma é obrigatória")
        .max(2, "Turma é no máximo 2 caracteres")
        .required("Turma é obrigatória"),
  });

  const initialValues = {
    nomeAluno: "",
    dataNascimento: "",
    serie: "",
    dataAtendimento: "",
    turma: "",
  };

  const handleSubmit = (itens : any) => {

  };

  const handleFormSubmit = (value : any) => {

    try {
      toggleChange(value);
    } catch(error) {
      console.log(error)
    } finally {
      setIsLoading(false)
    }
  }

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
                    className={`w-[389px] h-[52px] border ${errors.nomeAluno && touched.nomeAluno ? 'border-red-600' : 'border-gray-300'} rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                    placeholder="Nome do Aluno"
                  />
                  <ErrorMessage
                    name="nomeAluno"
                    component="div"
                    className="text-red-600 text-sm"
                  />
                </div>

                <div className="mb-4">
                  <label htmlFor="dataNascimento" className="hidden text-sm font-medium">
                    Data de Nascimento
                  </label>
                  <Field
                    name="dataNascimento"
                    render={({ field } : any) => (
                      <InputMask
                        {...field}
                        mask="99/99/9999" // Define a máscara para data no formato DD/MM/YYYY
                        type="text"
                        className={`w-[389px] h-[52px] border ${errors.dataNascimento && touched.dataNascimento ? 'border-red-600' : 'border-gray-300'} rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                        placeholder="Data de Nascimento"
                      />
                    )}
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
                    className={`w-[389px] h-[52px] border ${errors.serie && touched.serie ? 'border-red-600' : 'border-gray-300'} rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                    placeholder="Ano/Série"
                  />
                  <ErrorMessage
                    name="serie"
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
                    className={`w-[389px] h-[52px] border ${errors.turma && touched.turma ? 'border-red-600' : 'border-gray-300'} rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
                    placeholder="Turma"
                    maxLength={2}
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
                  disabled={!(isValid && dirty)}
                  onClick={() => handleFormSubmit(values)}
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
