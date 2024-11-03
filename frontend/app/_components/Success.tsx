import React from "react";

const Confirm: React.FC = () => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-80 z-50">
      <img src="/Success.png" alt="Success" className="opacity-100" />
    </div>
  );
}

export default Confirm;
