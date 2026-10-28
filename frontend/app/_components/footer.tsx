export const UNOFFICIAL_NOTICE =
  "Projeto acadêmico não oficial, sem vínculo com o Colégio Dom Bosco ou com o Grupo Dom Bosco e sem endosso dessas instituições.";

export const Footer = () => {
  return (
    <footer className="w-full bg-brand-ink px-5 py-6 text-center text-xs text-white">
      <p className="mx-auto max-w-2xl font-semibold">{UNOFFICIAL_NOTICE}</p>
      <p className="mx-auto mt-2 max-w-2xl">
        Desenvolvido por Emanuel Luis, Felipe (felipeoak1) e Tarcísio (tarcisio)
        como projeto de faculdade.
      </p>
    </footer>
  );
};
