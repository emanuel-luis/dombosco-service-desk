"use client";
import {
  CalendarIcon,
  HomeIcon,
  LogInIcon,
  LogOutIcon,
  MenuIcon,
  UserIcon,
} from "lucide-react";
import { signIn, signOut, useSession } from "next-auth/react";
import Image from "next/image";
import Link from "next/link";
import { Avatar, AvatarImage } from "./ui/avatar";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "./ui/sheet";

export const Header = () => {
  const { data, status } = useSession();

  return (
    <Card>
      <CardContent className="flex flex-row justify-between items-center bg-[#F6F5FC]">
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="p-2 hover:after:white"
            >
              <MenuIcon size={18} color="black" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 bg-white">
            <SheetHeader className="p-5 text-left border-b border-solid border-link">
              <SheetTitle>Menu</SheetTitle>
            </SheetHeader>

            {data?.user ? (
              <div className="flex justify-between px-5 py-6 items-center">
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarImage
                      src={data.user?.image ?? ""}
                      alt={data.user.name ?? ""}
                    />
                  </Avatar>
                  <h2 className="font-bold ">{data.user.name}</h2>
                </div>
                <Button
                  onClick={() => signOut({ callbackUrl: "/login" })}
                  variant="link"
                  size="icon"
                >
                  <LogOutIcon size={25} />
                </Button>
              </div>
            ) : (
              <div className=" flex flex-col px-5 py-6 gap-3">
                <div className="flex items-center gap-3  ">
                  <UserIcon />
                  <h2 className="font-bold">Olá,faça seu login!</h2>
                </div>
                <Button
                  variant="link"
                  className="w-full justify-start"
                  onClick={() => signIn()}
                >
                  <LogInIcon className="mr-2" size={15} />
                  Fazer Login
                </Button>
              </div>
            )}

            <div className="flex flex-col gap-3 px-5">
              <Button variant="link" className="justify-start" asChild>
                <Link href="/">
                  <HomeIcon size={18} className="mr-2" />
                  Inicio
                </Link>
              </Button>
              {data?.user && (
                <Button variant="default" className="justify-start" asChild>
                  <Link href="/bookings">
                    <CalendarIcon size={18} className="mr-2" />
                    Agendamentos
                  </Link>
                </Button>
              )}
            </div>
          </SheetContent>
        </Sheet>
        <Image src="/Logo.png" alt="logo" height={22} width={120} />
        <div></div>
      </CardContent>
    </Card>
  );
};
