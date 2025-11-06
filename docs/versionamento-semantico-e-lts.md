# Versionamento Semântico e LTS

### 1. Tailwind CSS

O Tailwind é um framework CSS utility-first.

* **Versionamento Semântico: Sim.**
    O projeto principal do Tailwind CSS segue o versionamento semântico. Eles reservam mudanças que quebram a retrocompatibilidade (breaking changes) para as versões principais (ex: v2.0, v3.0, v4.0).

* **LTS (Long-Term Support): Não.**
    Não há evidências de uma política oficial de "Long-Term Support" (LTS) para o Tailwind CSS. O projeto foca em fornecer guias de migração detalhados entre as versões principais, em vez de manter suporte estendido para versões antigas.

* **Evidência (Links):**
    * **Uso de SemVer (Documentação v1):** [Upcoming Changes - Tailwind CSS v1](https://v1.tailwindcss.com/docs/upcoming-changes) (Menciona: "Tailwind follows semantic versioning, so we never introduce breaking changes until a new major release...")
    * **Guia de Atualização (Evidência de Migração vs. LTS):** [Upgrade Guide - Tailwind CSS](https://tailwindcss.com/docs/upgrade-guide) (Demonstra o foco na atualização para a versão mais recente).

### 1. Pillow (Python Imaging Library fork)

`Pillow` é uma biblioteca fundamental para processamento de imagens em Python. Versão usada no projeto é a  `pillow==12.0.0`.

* **Versionamento Semântico: Sim.**
    O Pillow segue explicitamente o Versionamento Semântico. A versão `12.0.0` a versão usada no projeto indica uma *release* principal (MAJOR), que é onde eles introduzem mudanças que quebram a retrocompatibilidade (como a remoção de funções depreciadas ou a atualização de versões mínimas do Python).

* **LTS (Long-Term Support): Não.**
    O Pillow não possui uma política oficial de LTS. O projeto foca em lançamentos trimestrais. Correções de segurança e bugs críticos são geralmente aplicadas na *release* mais recente, e os usuários são encorajados a atualizar para ela, em vez de manter uma versão antiga com suporte estendido.

* **Evidência (Links):**
    * **Política de Versionamento (Oficial):** [Pillow Versioning Policy](https://pillow.readthedocs.io/en/stable/releasenotes/versioning.html) (Declara: "Pillow follows Semantic Versioning...")