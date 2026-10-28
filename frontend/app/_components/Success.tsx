import { useRouter } from "next/navigation";
import React from "react";
import Image from "next/image";
import { BackArrow } from "./BackArrow";

const Confirm: React.FC = () => {
  const router = useRouter()
  return (
    
    <div className="fixed inset-0 flex items-center justify-center bg-foreground/80 z-50">
      <button onClick={() => router.push('/')} className="text-primary mb-5"><BackArrow /></button>
      <Image src="/Success.png" alt="Solicitação enviada com sucesso" width={268} height={137} />
    </div>
  );
}

export default Confirm;
