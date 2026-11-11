/**
 * Fronteiras de arquitetura (roda com `npm run lint:arquitetura`).
 *
 *   modules/<id>/domain          regras de negócio puras. Não conhece mais nada do módulo.
 *   modules/<id>/application     casos de uso e portas (interfaces). Não conhece infraestrutura nem interface.
 *   modules/<id>/infrastructure  API, banco, dados de exemplo. Implementa as portas.
 *   modules/<id>/presentation    telas, componentes e hooks.
 *   shared/                      o que é de todos. Não conhece os módulos.
 *
 * Um módulo nunca importa outro módulo.
 */
/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: 'dominio-nao-depende-do-resto-do-modulo',
      comment: 'O domínio é puro: não importa application, infrastructure nem presentation.',
      severity: 'error',
      from: { path: '^src/modules/([^/]+)/domain/' },
      to: { path: '^src/modules/$1/(application|infrastructure|presentation)/' },
    },
    {
      name: 'aplicacao-nao-depende-de-infraestrutura-nem-interface',
      comment: 'Casos de uso falam com portas (interfaces), nunca com a implementação nem com a tela.',
      severity: 'error',
      from: { path: '^src/modules/([^/]+)/application/' },
      to: { path: '^src/modules/$1/(infrastructure|presentation)/' },
    },
    {
      name: 'modulo-nao-importa-outro-modulo',
      comment: 'Um módulo não importa outro. O que for comum vai para src/shared.',
      severity: 'error',
      from: { path: '^src/modules/([^/]+)/' },
      to: { path: '^src/modules/', pathNot: '^src/modules/$1/' },
    },
    {
      name: 'shared-nao-conhece-os-modulos',
      severity: 'error',
      from: { path: '^src/shared/' },
      to: { path: '^src/modules/' },
    },
    {
      name: 'sem-dependencia-circular',
      severity: 'warn',
      from: {},
      to: { circular: true },
    },
  ],
  options: {
    doNotFollow: { path: 'node_modules' },
    tsPreCompilationDeps: true,
    tsConfig: { fileName: 'tsconfig.app.json' },
  },
};
