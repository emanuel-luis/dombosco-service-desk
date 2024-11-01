"use client"

const Loader = ({ isLoading }: { isLoading: any }) => {
  if (!isLoading) {
    return null;
  }

  return (
    <>
      <div className="fixed inset-0 flex items-center justify-center bg-gray-200 bg-opacity-70 z-50">
        <div className="loader w-16 h-16 border-8 border-t-8 border-t-primary rounded-full animate-load animate-round"></div>
      </div>
    </>
  )

}


export default Loader;
