"use client";
import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Button } from "./ui/button"; 
import { Textarea } from "./ui/textarea"; 
import * as Yup from 'yup';


const Treatment = ({handleUserSubmit, handleBack} : any) => {

  const initialValues = {
    tratativa: "", 
  };

  const handleSubmit = (values : any) => {
    console.log("Formulário enviado:", values);

  };

  const validationSchema = Yup.object({
    tratativa: Yup.string()
    .required('O campo tratativa é obrigatório')
  })

  return (
    <>

    <div className="flex justify-center items-center">
      <div className="w-full max-w-md px-5 pt-5">
        <h2 className="text-xl font-bold text-left mb-8">Tratativas</h2>
        <Formik  validationSchema={validationSchema} initialValues={initialValues} onSubmit={handleSubmit}>
          {({ values, errors, touched, dirty, isValid}) => (
            <Form>
              <div className="mb-4">
                <label
                  htmlFor="tratativa"
                  className="hidden text-sm font-medium"
                >
                  Tratativa
                </label>
                <Field name="tratativa" >
                  {({ field } : any) => (
                    <Textarea
                      {...field}
                      className={`w-[389px] h-[52px] border ${
                        errors.tratativa && touched.tratativa ? 'border-red-600' : 'border-gray-300'
                      } rounded-[4px] p-3 bg-white shadow-[0_4px_10px_0_rgba(0,0,0,0.04)] hover:border-blue-500 outline-none`}
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
                type="button"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
                onClick={() => handleUserSubmit(values)}
                disabled={!(isValid && dirty)}
              >
                Avançar
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
