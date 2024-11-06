"use client";
import { HomeIcon, LogOutIcon, MenuIcon, UserIcon } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "./ui/sheet";
import { useContext } from "react";
import { AuthContext, AuthContextType } from "../context/authContext";
import { useRouter } from "next/navigation";

export const Header = ({ showMenuButton = true }) => {
  const { logout, isAuthenticated } = useContext<AuthContextType>(AuthContext);
  const router = useRouter(); // Inicializando o router

  const handleLogout = () => {
    logout(); // Chama a função de logout
    router.push("/login"); // Redireciona para a página de login
  };

  return (
    <Card>
      <CardContent className="flex flex-row justify-between items-center bg-[#F6F5FC]">
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className={`p-2 hover:after:white ${
                showMenuButton ? "" : "invisible"
              }`} // Torna o botão invisível
            >
              <MenuIcon size={18} color="black" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 bg-white">
            <SheetHeader className="p-5 text-left border-b border-solid border-link">
              <SheetTitle>Menu</SheetTitle>
            </SheetHeader>

            {isAuthenticated ? ( // Verifica se o usuário está autenticado
              <div className="flex justify-between px-5 py-6 items-center">
                <div className="flex items-center gap-3">
                  {/* <Avatar>
                    <AvatarImage
                      src=
                      alt=
                    />
                  </Avatar> */}
                  <h2 className="font-bold "></h2>
                </div>
                <Button
                  onClick={() => router.push("/login")}
                  variant="link"
                  size="icon"
                >
                  <LogOutIcon size={25} />
                </Button>
              </div>
            ) : (
              <div className="flex flex-col px-5 py-6 gap-3">
                <div className="flex items-center gap-3">
                  <UserIcon />
                  <h2 className="font-bold">Olá, faça seu login!</h2>
                </div>
              </div>
            )}

            <div className="flex flex-col gap-3 px-5">
              <Button variant="link" className="justify-start" asChild>
                <Link href="/login">
                  <HomeIcon size={18} className="mr-2" />
                  Início
                </Link>
              </Button>
            </div>
            <div className="flex flex-col gap-3 px-5">
              <Button
                variant="link"
                onClick={handleLogout} // Chama a função handleLogout ao clicar
                className="justify-start"
                asChild
              >
                <Link href="#">
                  <LogOutIcon size={18} className="mr-2" />
                  Logout
                </Link>
              </Button>
            </div>
          </SheetContent>
        </Sheet>
        <Image src="/Logo.png" alt="logo" height={22} width={120} />
        <div></div>
      </CardContent>
    </Card>
  );
};
