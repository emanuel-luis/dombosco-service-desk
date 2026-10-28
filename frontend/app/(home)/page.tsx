"use client";

import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import Card from "../_components/Card";
import { Header } from "../_components/header";
import formsServices from "../services/ContactsService";
import { useEffect, useState } from "react";
import Loader from "../_components/loader";

interface User {
  first_name: string;
  last_name: string;
  email: string;
}

export default function Home() {
  const [user, setUser] = useState<User[]>([]);
  const [group, setGroup] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getUser = async () => {
      try {
        const data = await formsServices.listUser();
        setUser((prevState) => [...prevState, data]);
        setIsLoading(false);
      } catch (error) {
        console.log(error);
      } finally {
        setIsLoading(false);
      }
    };
    getUser();
  }, []);

  useEffect(() => {
    const getApllication = async () => {
      try {
        const data = await formsServices.listAplications();
        setGroup(data);
        setIsLoading(false);
      } catch (error) {
        console.log(error);
      } finally {
        setIsLoading(false);
      }
    };
    getApllication();
  }, []);

  return (
    <>
      {isLoading ? (
        <Loader isLoading />
      ) : (
        <>
          <Header />
          <div className="px-5 pt-5 max-w-screen-lg mx-auto">
            <h2 className="text-xl font-bold">{user[0]?.first_name}</h2>
            <p className="capitalize text-sm">
              {format(new Date(), "EEEE, d 'de' MMMM", { locale: ptBR })}
            </p>
            <div className="flex flex-wrap -m-4">
              {/* CRIAR TRATAMENTO PARA ERROS DA API */}
              {group?.map((data) => (
                <div key={data["name"]} className="w-1/3 p-4 my-4">
                  <Card
                    title={data["name"]}
                    description={data["description"]}
                    icon={data["mdm_id"]}
                    link={`/petitions`}
                  />
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </>
  );
}
