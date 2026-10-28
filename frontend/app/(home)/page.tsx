"use client";

import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import Card from "../_components/Card";
import { Header } from "../_components/header";
import { useEffect, useState } from "react";
import Loader from "../_components/loader";
import { useAuth } from "../context/authContext";
import { api } from "../lib/api";
import { toMessage } from "../lib/errors";
import { Application } from "../lib/types";

export default function Home() {
  const { user, userLoading } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listApplications()
      .then(setApplications)
      .catch((e) => setError(toMessage(e)))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <>
      {isLoading || userLoading ? (
        <Loader isLoading />
      ) : (
        <>
          <Header />
          <div className="px-5 pt-5 max-w-screen-lg mx-auto">
            <h2 className="text-xl font-bold">{user?.first_name}</h2>
            <p className="capitalize text-sm">
              {format(new Date(), "EEEE, d 'de' MMMM", { locale: ptBR })}
            </p>
            {error && (
              <p role="alert" className="text-destructive text-sm mt-4">
                {error}
              </p>
            )}
            <div className="flex flex-wrap -m-4">
              {applications.map((app) => (
                <div key={app.id} className="w-1/3 p-4 my-4">
                  <Card
                    title={app.name}
                    description={app.description ?? ""}
                    icon={app.mdm_id}
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
