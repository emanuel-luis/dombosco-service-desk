"use client"; // Indica que este é um componente de cliente
import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "../_components/ui/button";
import { Header } from "../_components/header";

const validationSchema = z.object({
  nome: z.string().min(1, "Nome é obrigatório"),
  dataNascimento: z
    .date()
    .max(new Date(), "Data de nascimento deve ser no passado")
    .nullable(),
  serie: z.string().min(1, "Ano/Série é obrigatório"),
  dataAtendimento: z
    .date()
    .max(new Date(), "Data de atendimento deve ser no máximo hoje")
    .nullable(),
  turma: z.string().min(1, "Turma é obrigatória"),
});

const AlunoForm = () => {
  const [isDisable, setIsDisable] = useState(false)

  const initialValues = {
    nome: "",
    dataNascimento: "",
    serie: "",
    dataAtendimento: "",
    turma: "",
  };

  const handleSubmit = (values: any) => {
    
    console.log("Formulário enviado:", values);
    // Aqui você pode fazer uma requisição para enviar os dados
  };

  return (
    <>
    
    <Header />
    <div className="flex justify-center items-center">
      <div className="w-full max-w-md px-5 pt-5">
      <button className="text-[#5061FC] mb-5">Voltar</button>
        <h2 className="text-xl font-bold text-left mb-8">Formulário de Aluno</h2>
        <Formik initialValues={initialValues} onSubmit={handleSubmit}>
          {() => (
            <Form>
              <div className="mb-4">
                <label htmlFor="nome" className="hidden text-sm font-medium">
                  Nome
                </label>
                <Field
                  name="nome"
                  type="text"
                  className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] 
                  hover:border-blue-500"
                  placeholder="Nome"
                />
                <ErrorMessage
                  name="nome"
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
                  type="date"
                  className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] 
                  hover:border-blue-500"
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
                  className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] 
                  hover:border-blue-500"
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
                  className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] 
                  hover:border-blue-500"
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
                  className="w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] 
                  hover:border-blue-500"
                  placeholder="Turma"
                />
                <ErrorMessage
                  name="turma"
                  component="div"
                  className="text-red-600 text-sm"
                />
              </div>

              <Button
                type="submit"
                className={`${isDisable ? "bg-[#BCBCBC]" : "bg-[#5061FC]"} w-[389px] h-[52px] border border-gray-300 rounded-[4px] p-3 shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] mt-8 text-white`}
                // Adicionando largura total ao botão
                disabled={!isDisable}
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
