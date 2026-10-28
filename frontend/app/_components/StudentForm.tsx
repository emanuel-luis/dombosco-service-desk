"use client"; 
import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Button } from "./ui/button";
import useLoginValidation from "../utils/loginValidation"
import InputMask from 'react-input-mask'
import Loader from "./loader";
import * as Yup from "yup"
import { isPlausibleBirthDate } from "../lib/birthDate"

const AlunoForm = ({toggleChange, formValues} : any) => {
  useLoginValidation()

  const [isDisable, setIsDisable] = useState(false)
  const [formInfo, setFormInfo] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  const validationSchema = Yup.object({
    nomeAluno: Yup.string()
        .required('Campo nome é obrigatório'),
    dataNascimento: Yup.string()
        .required("Data de nascimento é obrigatória")
        .test("plausible-date", "Informe uma data de nascimento válida (DD/MM/AAAA).", (value) =>
          !!value && isPlausibleBirthDate(value)
        ),
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
                    className={`w-[389px] h-[52px] border ${errors.nomeAluno && touched.nomeAluno ? 'border-destructive' : 'border-input'} rounded-[4px] p-3 bg-card shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-primary outline-none`}
                    placeholder="Nome do Aluno"
                  />
                  <ErrorMessage
                    name="nomeAluno"
                    component="div"
                    className="text-destructive text-sm"
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
                        className={`w-[389px] h-[52px] border ${errors.dataNascimento && touched.dataNascimento ? 'border-destructive' : 'border-input'} rounded-[4px] p-3 bg-card shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-primary outline-none`}
                        placeholder="Data de Nascimento"
                      />
                    )}
                  />
                  <ErrorMessage
                    name="dataNascimento"
                    component="div"
                    className="text-destructive text-sm"
                  />
                </div>

                <div className="mb-4">
                  <label htmlFor="serie" className="hidden text-sm font-medium">
                    Ano/Série
                  </label>
                  <Field
                    name="serie"
                    type="text"
                    className={`w-[389px] h-[52px] border ${errors.serie && touched.serie ? 'border-destructive' : 'border-input'} rounded-[4px] p-3 bg-card shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-primary outline-none`}
                    placeholder="Ano/Série"
                  />
                  <ErrorMessage
                    name="serie"
                    component="div"
                    className="text-destructive text-sm"
                  />
                </div>

                <div className="mb-4">
                  <label htmlFor="turma" className="hidden text-sm font-medium">
                    Turma
                  </label>
                  <Field
                    name="turma"
                    type="text"
                    className={`w-[389px] h-[52px] border ${errors.turma && touched.turma ? 'border-destructive' : 'border-input'} rounded-[4px] p-3 bg-card shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-primary outline-none`}
                    placeholder="Turma"
                    maxLength={2}
                  />
                  <ErrorMessage
                    name="turma"
                    component="div"
                    className="text-destructive text-sm"
                  />
                </div>

                <Button
                  type="button"
                  className={`${isDisable ? "bg-muted-foreground" : "bg-primary"} w-[389px] h-[52px] border border-input rounded-[4px] p-3 shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] mt-8 text-white`}
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
