"use client"
import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "../_components/ui/select";
import { Textarea } from "../_components/ui/textarea";
import { Button } from "../_components/ui/button";
import { Header } from "../_components/header";

const PersonsResponsibleForm = () => {
  const [isDisable, setIsDisable] = useState(false);
  const [showTratativa, setShowTratativa] = useState(false); // Novo estado para alternar entre os formulários

  const initialValues = {
    nome: "",
    solicitado: "",
    parentesco: "",
    email: "",
    phone: "",
    tratativa: "",
  };

  const handleSubmit = (values) => {
    console.log("Formulário enviado:", values);
    // Lógica para envio de dados
  };

  const handleAdvance = () => {
    setShowTratativa(true);
  };

  const handleBack = () => {
    setShowTratativa(false);
  };

  return  (
    <>
      <Header />
      <div className="flex justify-center items-center w-full">
        <div className="w-full max-w-md px-5 pt-5">
          <button className="text-[#5061FC] mb-5">Voltar</button>
          <h2 className="text-xl font-bold text-left mb-8">
            Formulário de Responsável
          </h2>

          <Formik initialValues={initialValues} onSubmit={handleSubmit}>
            {({ values, setFieldValue, handleBlur }) => (
              <Form>
                {/* Exibe os campos iniciais ou o campo Tratativa */}
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

                    {/* Botão para avançar ao campo Tratativa */}
                    <Button                    
                      type="button"
                      onClick={handleAdvance}
                      className="bg-[#5061FC] w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] mt-8 text-white"
                    >
                      Avançar
                    </Button>
                  </>
                ) : (
                  <>
                    {/* Campo Tratativa */}
                    <div className="mb-4">
                      <label htmlFor="tratativa" className="hidden text-sm font-medium">
                        Tratativa
                      </label>
                      <Field name="tratativa">
                        {({ field }) => (
                          <Textarea
                            {...field}
                            className="mt-1 block w-full border border-gray-300 rounded-md p-2 bg-white text-gray-800 placeholder-gray-500"
                            placeholder="Digite sua tratativa aqui..."
                          />
                        )}
                      </Field>
                      <ErrorMessage name="tratativa" component="div" className="text-red-600 text-sm" />
                    </div>

                    {/* Botões de Voltar e Enviar */}
                    <Button
                      type="button"
                      onClick={handleBack}
                      className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded w-full mb-4"
                    >
                      Voltar
                    </Button>
                    <Button
                      type="submit"
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
                    >
                      Enviar
                    </Button>
                  </>
                )}
              </Form>
            )}
          </Formik>
        </div>
      </div>
    </>
  );
};

export default PersonsResponsibleForm;
