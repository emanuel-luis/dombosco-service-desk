'use client'

import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import Card from "../_components/Card";
import { Header } from "../_components/header";
import formsServices from "../services/ContactsService";
import { useEffect, useState } from "react";
import { groupCollapsed } from "console";
//

export default function Home() {
  const [userRole, setUserRole] = useState([])
  const [application, setApplication] = useState([])
  const [user, setUser] = useState([])
  const [group, setGroup] = useState([])


  useEffect(() => {
    const getUser = async () => {
      try {
        const data = await formsServices.listUsers()
        const parsedName = data.last_name.split(' ')
        setUser(prevState => [...prevState, data])
        setUserRole(parsedName === '(PARENT)' ? 1 : 2)
      } catch(error) {
        console.log(error)
      }
    }
    getUser()
  }, [])
  
  console.log(user[0])

  useEffect (() => {
    if (userRole) {
      const getApllication = async () => {
        try {
          const data = await formsServices.listAplications()
          console.log(data)
          const matchingGroups = data.filter(c => c?.groups.includes(userRole))
          setGroup(matchingGroups)
          setApplication(prevState => [...prevState, ...data])
          } catch(error) {
          console.log(error)
        }
      }
      getApllication()
    }
  }, [userRole])

  return (
    <>
      <Header />
      <div className="px-5 pt-5 max-w-screen-lg mx-auto">
        <h2 className="text-xl font-bold">{user?.first_name}</h2>
        <p className="capitalize text-sm">
          {format(new Date(), "EEEE, d 'de' MMMM", { locale: ptBR })}
        </p>
        <div className="flex flex-wrap -m-4"> {/* Removi o min-w-1000px para permitir responsividade */}
          {/* CRIAR TRATAMENTO PARA ERROS DA API */}
          <div><a href="/petitions/1">clique aqui</a></div>
          {group.map((data) => (
            <div key={Math.random()} className="w-1/3 p-4 my-4"> 
              <Card
                title={data['name']}
                description={data['description']}
                icon={data['mdm_id']}
                link={`/petitions/${Number(user[0]['pk'])}`}
              />
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
