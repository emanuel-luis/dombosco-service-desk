import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import Card from "../_components/Card";
import { Header } from "../_components/header";

export default async function Home() {
  return (
    <>
      <Header />
      <div className="px-5 pt-5 max-w-screen-lg mx-auto"> {/* Limite de largura de 1000px */}
        <h2 className="text-xl font-bold">Olá Tarcisio </h2>
        <p className="capitalize text-sm">
          {format(new Date(), "EEEE, d 'de' MMMM", { locale: ptBR })}
        </p>
        <div className="flex flex-wrap -m-4 min-w-[1000px]">
          {/* Configura a grade 3x3 com margem de 16px em cima e embaixo */}
          <div className="w-1/3 p-4 my-4"> {/* Margem vertical de 16px */}
            <Card
              title="Cartão 1"
              description="Descrição do cartão 1"
              icon="" // Substitua por um ícone se necessário
              link="/petitions"
            />
          </div>
          <div className="w-1/3 p-4 my-4"> {/* Margem vertical de 16px */}
            <Card
              title="Cartão 2"
              description="Descrição do cartão 2"
              icon="" // Substitua por um ícone se necessário
            />
          </div>
          <div className="w-1/3 p-4 my-4"> {/* Margem vertical de 16px */}
            <Card
              title="Cartão 3"
              description="Descrição do cartão 3"
              icon="" // Substitua por um ícone se necessário
            />
          </div>
          <div className="w-1/3 p-4 my-4"> {/* Margem vertical de 16px */}
            <Card
              title="Cartão 4"
              description="Descrição do cartão 4"
              icon="" // Substitua por um ícone se necessário
            />
          </div>
          <div className="w-1/3 p-4 my-4"> {/* Margem vertical de 16px */}
            <Card
              title="Cartão 5"
              description="Descrição do cartão 5"
              icon="" // Substitua por um ícone se necessário
            />
          </div>
        </div>
      </div>

    </>
  );
}
