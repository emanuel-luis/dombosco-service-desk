"use client";
import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { z } from "zod";
import { Button } from "../_components/ui/button"; // Importing the button from ShadCN
import { Textarea } from "../_components/ui/textarea"; // Importing the Textarea from ShadCN
import { Header } from "../_components/header";

const validationSchema = z.object({
  tratativa: z.string().min(1, "Tratativa é obrigatória"), // Adding validation for tratativa
});

const Treatment = () => {
  const initialValues = {
    tratativa: "", // Initializing as an empty string
  };

  const handleSubmit = (values) => {
    console.log("Formulário enviado:", values);
    // Here you can make a request to send the data
  };

  return (
    <>

    <Header />
    <div className="flex justify-center items-center">
      <div className="w-full max-w-md px-5 pt-5">
        <h2 className="text-xl font-bold text-left mb-8">Tratativas</h2>
        <Formik initialValues={initialValues} onSubmit={handleSubmit}>
          {() => (
            <Form>
              <div className="mb-4">
                <label
                  htmlFor="tratativa"
                  className="hidden text-sm font-medium"
                >
                  Tratativa
                </label>
                <Field name="tratativa" >
                  {({ field }) => (
                    <Textarea
                      {...field}
                      className="mt-1 block w-full border border-gray-300 rounded-md p-2 bg-white text-gray-800 placeholder-gray-500" // Customize colors here
                      placeholder="Digite sua tratativa aqui..."
                    />
                  )}
                </Field>
                <ErrorMessage
                  name="tratativa"
                  component="div"
                  className="text-red-600 text-sm"
                />
              </div>

              <Button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
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

export default Treatment;
