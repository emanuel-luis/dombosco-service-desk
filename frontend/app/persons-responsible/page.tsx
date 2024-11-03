"use client"

import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "../_components/ui/select";
import { Textarea } from "../_components/ui/textarea";
import { Button } from "../_components/ui/button";
import { Header } from "../_components/header";
import AlunoForm from "../studentform/page";
import formsServices from "../services/ContactsService";
import Confirm from "../_components/Success";
import Loader from "../_components/loader";

const PersonsResponsibleForm =  () => {
  const [responseTrue, setResponseTrue] = useState(false);
  const [showTratativa, setShowTratativa] = useState(false);
  const [studentForm, setStudentForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false)
  

  const initialValues = {
    nome: "",
    solicitado: "",
    parentesco: "",
    email: "",
    phone: "",
    tratativa: "",
  };

  const handleSubmit = () => {
    console.log("Formulário enviado da onde não era pra enviar")
  };

  const handleAdvance = () => {
    setShowTratativa(true);
  };

  const handleBack = () => {
    setShowTratativa(false);
  };

  const showStudentForm = () => {
    setStudentForm(true)
  }

  const toggleChange = async (data : any) => {
    setIsLoading(true)

    try {
      await formsServices.createForm(data)
      setResponseTrue(true)
    } catch(error) {
      console.log(error)
    } finally {
      setIsLoading(false)
    }
  }

  return  (
    <>
      <Header />
      <div className="flex justify-center items-center w-full">
        <div className="w-full max-w-md px-5 pt-5">
          <button className="text-[#5061FC] mb-5">Voltar</button>
          <h2 className="text-xl font-bold text-left mb-8">
            {!studentForm ? "Formulário de Responsável" : "Formulário do Aluno"}
          </h2>

          <Formik initialValues={initialValues} onSubmit={handleSubmit}>
            {({ values, setFieldValue, handleBlur }) => ( 
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
                        className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500"
                        placeholder="Nome"
                        required
                      />
                      <ErrorMessage name="nome" component="div" className="text-red-600 text-sm" />
                    </div>

                    <div className="mb-4">
                      <label htmlFor="parentesco" className="hidden text-sm font-medium">
                        Grau de Parentesco
                      </label>
                      <Field
                        name="parentesco"
                        className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500"
                        placeholder="Grau de Parentesco"
                      />
                    </div>

                    <div className="mb-4">
                      <label htmlFor="email" className="hidden text-sm font-medium">
                        Email
                      </label>
                      <Field
                        name="email"
                        type="email"
                        className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500"
                        placeholder="E-mail"
                      />
                    </div>

                    <div className="mb-4">
                      <label htmlFor="phone" className="hidden text-sm font-medium">
                        Telefone
                      </label>
                      <Field
                        name="phone"
                        type="phone"
                        className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500"
                        placeholder="Telefone"
                      />
                    </div>

                    <div className="mb-4">
                      <label htmlFor="solicitado" className="hidden text-sm font-medium">
                        Solicitado
                      </label>
                      <Field name="solicitado">
                        {() => (
                          <Select onValueChange={(value) => setFieldValue("solicitado", value)}>
                            <SelectTrigger className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-4 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500">
                              <SelectValue placeholder="Selecione uma opção" />
                            </SelectTrigger>
                            <SelectContent className="bg-[white]">
                              <SelectItem value="light" className="border border-gray-300">Light</SelectItem>
                              <SelectItem value="dark" className="border border-gray-300">Dark</SelectItem>
                              <SelectItem value="system" className="border border-gray-300">System</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                      </Field>
                      <ErrorMessage name="solicitado" component="div" className="text-red-600 text-sm" />
                    </div>

                    <Button                    
                      type="button"
                      onClick={(values : any) => handleAdvance()}
                      className="bg-[#5061FC] w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] mt-8 text-white"
                    >
                      Avançar
                    </Button>
                  </>
                ) : !studentForm ? (
                  <>
                    {/* Campo Tratativa */}
                    <div className="mb-4">
                      <label htmlFor="tratativa" className="hidden text-sm font-medium">
                        Tratativa
                      </label>
                      <Field name="tratativa">
                        {({ field }:{field:any}) => (
                          <Textarea
                            {...field}
                            className="mt-1 block w-full border border-gray-300 rounded-md p-2 bg-white text-gray-800 placeholder-gray-500"
                            placeholder="Digite sua tratativa aqui..."
                          />
                        )}
                      </Field>
                      <ErrorMessage name="tratativa" component="div" className="text-red-600 text-sm" />
                    </div>

                    <Button
                      type="button"
                      onClick={handleBack}
                      className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded w-full mb-4"
                    >
                      Voltar
                    </Button>
                    <Button
                      type="button"
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
                      onClick={showStudentForm}
                    >
                      Enviar
                    </Button>
                  </>
                ) : responseTrue ? <Confirm /> : isLoading ? <Loader isLoading /> : <AlunoForm 
                        toggleChange={toggleChange}
                        formValues={values}
                    /> }
              </Form>
            )}

          </Formik>
        </div>
      </div>
      
    </>
  );
};

export default PersonsResponsibleForm;
