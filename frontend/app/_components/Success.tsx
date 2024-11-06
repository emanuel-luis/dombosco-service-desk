import { useRouter } from "next/navigation";
import React, { useReducer } from "react";

const Confirm: React.FC = () => {
  const router = useRouter()
  return (
    
    <div className="fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-80 z-50">
      <button onClick={() => router.push('/')} className="text-[#5061FC] mb-5"><img className="-rotate-90" src="/arrow.svg"/></button>
      <img src="/Success.png" alt="Success" className="opacity-100" />
    </div>
  );
}

export default Confirm;
