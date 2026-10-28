"use client";
import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { Button } from "../_components/ui/button";
import { useRouter } from "next/navigation";

const CreateAccount = () => {
  const router = useRouter();

  const validationSchema = Yup.object().shape({
    email: Yup.string().email("Email inválido").required("Email é obrigatório"),
    password1: Yup.string()
      .min(6, "A senha deve ter pelo menos 6 caracteres")
      .required("Senha é obrigatória"),
    password2: Yup.string()
      .oneOf([Yup.ref("password1")], "As senhas devem corresponder")
      .required("Confirmação de senha é obrigatória"),
    first_name: Yup.string().required("Primeiro nome é obrigatório"),
    last_name: Yup.string().required("Sobrenome é obrigatório"),
  });

  const handleSubmit = (values: any) => {
    // Aqui você pode fazer a chamada para a API ou qualquer outra lógica
    console.log(values);
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] bg-muted">
      <div className="bg-card p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Criar Conta</h1>
        <Formik
          initialValues={{
            email: "",
            password1: "",
            password2: "",
            first_name: "",
            last_name: "",
            mobile_phone: "",
          }}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {() => (
            <Form>
              <div className="mb-4">
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-brand-text"
                >
                  Email:
                </label>
                <Field
                  type="email"
                  name="email"
                  className="mt-1 block w-full border border-input rounded-md p-2"
                />
                <ErrorMessage
                  name="email"
                  component="div"
                  className="text-destructive text-sm"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="password1"
                  className="block text-sm font-medium text-brand-text"
                >
                  Senha:
                </label>
                <Field
                  type="password"
                  name="password1"
                  className="mt-1 block w-full border border-input rounded-md p-2"
                />
                <ErrorMessage
                  name="password1"
                  component="div"
                  className="text-destructive text-sm"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="password2"
                  className="block text-sm font-medium text-brand-text"
                >
                  Confirme a Senha:
                </label>
                <Field
                  type="password"
                  name="password2"
                  className="mt-1 block w-full border border-input rounded-md p-2"
                />
                <ErrorMessage
                  name="password2"
                  component="div"
                  className="text-destructive text-sm"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="first_name"
                  className="block text-sm font-medium text-brand-text"
                >
                  Primeiro Nome:
                </label>
                <Field
                  type="text"
                  name="first_name"
                  className="mt-1 block w-full border border-input rounded-md p-2"
                />
                <ErrorMessage
                  name="first_name"
                  component="div"
                  className="text-destructive text-sm"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="last_name"
                  className="block text-sm font-medium text-brand-text"
                >
                  Sobrenome:
                </label>
                <Field
                  type="text"
                  name="last_name"
                  className="mt-1 block w-full border border-input rounded-md p-2"
                />
                <ErrorMessage
                  name="last_name"
                  component="div"
                  className="text-destructive text-sm"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="mobile_phone"
                  className="block text-sm font-medium text-brand-text"
                >
                  Telefone Móvel:
                </label>
                <Field
                  type="text"
                  name="mobile_phone"
                  className="mt-1 block w-full border border-input rounded-md p-2"
                />
                <ErrorMessage
                  name="mobile_phone"
                  component="div"
                  className="text-destructive text-sm"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-primary hover:bg-primary/90 text-white font-bold py-2 px-4 rounded transition duration-200"
              >
                Criar Conta
              </button>
              <div className="flex items-center justify-center mt-2">
                <Button
                  type="button"
                  onClick={() => router.back()}
                  variant="link"
                >
                  Voltar
                </Button>
              </div>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default CreateAccount;
