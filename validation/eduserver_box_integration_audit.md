# Auditoria de projeto — eduServer Box — gate: conceito / antes do CAD — 18/11/2026

Teste de integração da skill `cad-design-audit` sobre artefatos reais do repositório `dasilva-thiago/server_box` (commit 9b1460f). Nenhum arquivo do projeto foi alterado. Os achados abaixo são do projeto; as regras gerais ficam na skill.

## 1. Cobertura

**Lidos (artefatos reais):**
- `docs/00_ESTADO_DO_PROJETO.md` (sessão 10, decisões 1–20);
- `docs/01_evidence_review_and_measurement_register.md` (R49);
- `docs/02_tolerancias.md` (T4);
- `docs/03_desenho_tecnico_placa.md` (D2);
- `docs/04_interfaces_eletricas.md` (E3);
- `docs/05_auditorias.md` (A3);
- `docs/06_decisoes_de_hardware.md` (H13);
- `docs/conceito/SNAP_FIT_*`;
- o conceito 3D `docs/conceito/caixa_3d/` (geometria ilustrativa, não CAD);
- `buy_list.md` (B28) e `CLAUDE.md`.

**Ferramentas rodadas:**
- `scripts/stack_up.py` em 3 cadeias do lábio (`validation/eduserver_chains/*.json`, saídas `*.out.json`);
- `scripts/mesh_audit.py` num envelope sintético de 208,25 × 165 × 24 (teste `test_bed_fit_with_and_without_brim_margin`).

**Não disponíveis:**
- **não existe CAD da caixa** (fase 3 não começou);
- a sessão do Fusion estava desconectada (MCP recusado);
- não há STEP nem STL das peças;
- o fornecedor e o material (PETG ou ASA) não estão escolhidos.

O `cad/n1110_placa.dxf` não foi aberto nesta auditoria: a conferência da importação no Fusion consta do `00` §8.2 (DOCUMENTADO, NÃO VERIFICADO por esta auditoria).

**Consequência:** o domínio A (integridade geométrica) não pôde ser executado; os achados dos outros domínios vêm de documentos, decisões e cálculos.

## 2. Veredito

**APROVADO COM CONDIÇÕES** para continuar na fase 2 (arquitetura). **Não aprovado** para o portão "Pronto para modelar", que o próprio projeto ainda não declara cumprido.

| BLOCKER abertos | MAJOR abertos | MINOR | OBSERVAÇÃO | BLOCKED (dados) |
|---|---|---|---|---|
| 0 | 6 | 3 | 1 | 3 |

Decidem o veredito:
- o orçamento do lábio tampa/base não fecha no pior caso (C-01);
- a escolha do material depende de um teste térmico que está marcado para depois da impressão (B-02);
- o requisito de segurança contra fogo não está definido (D-02).

## 3. Achados

### C-01 · MAJOR · O lábio tampa/base pode interferir no pior caso
- **Componente:** lábio entre a base e a tampa principais (`02` §5.7; decisão 1).
- **Problema:** a folga de 0,35 por lado foi orçada com a classe m da faixa de **0,5 a 3 mm** (espessura do lábio). Mas o encaixe varia com o **contorno do lábio**, de ≈ 165 a 208 mm (decisão 20), que fica na faixa de 120 a 400 mm. Além disso, o `02` §4.3 diz que, **sem cupom**, a premissa é a classe c; o §5.7 usa a m. Os dois trechos se contradizem.
- **Por que importa:** com interferência, a tampa não fecha ou força as colunas dos insertos.
- **Evidência (`stack_up.py`, folga total no contorno, 2 × 0,35 = 0,7):**

  | Cadeia | Pior caso, mín. | RSS, mín. |
  |---|---|---|
  | Como orçado (§5.7, por lado) | +0,15 | +0,21 |
  | Classe m, 120–400 mm, peças independentes | **−0,30** | −0,01 |
  | Classe c, sem cupom (premissa do §4.3) | **−1,70** | −1,00 |

  Os valores da ISO 2768 vêm de tabelas secundárias (S10); a largura nominal de 165 é ilustrativa, só a faixa importa.
- **Premissas e incerteza:**
  - as duas peças saem do mesmo fornecedor e material, então o erro de escala é em parte **correlacionado** e tende a se cancelar;
  - a parte não correlacionada da variação **não está quantificada** em nenhum documento;
  - o cupom G2 previsto ("um canto do lábio", `02` §6) não mede variação num vão de 200 mm.
- **Correção recomendada (escolher uma):**
  1. localizar a tampa em **poucos apoios curtos** (pinos ou abas de centragem em 2 ou 3 pontos) em vez de um lábio contínuo justo no perímetro, deixando o lábio com folga maior, só como vedação visual;
  2. incluir no cupom G2 uma **feature longa** (≥ 150 mm), ou pedir a primeira base e a primeira tampa antes do lote, e definir a folga pela medição;
  3. orçar com a classe declarada pelo fornecedor para 120–400 mm.
- **Verificação:** cadeia refeita com a tolerância do fornecedor; encaixe a seco da primeira peça (G3).
- **Status:** ABERTO.

### B-01 · MAJOR · Ressaltos da ventoinha com parafuso autoatarraxante no eixo Z
- **Componente:** anel-suporte com 4 ressaltos na tampa (decisão 12).
- **Problema:** a tampa é impressa de cabeça para baixo (decisão 20), e o anel, se for peça separada, é impresso deitado. Nos dois casos, o eixo do parafuso fica no eixo Z. Assim, o arrancamento e o aperto do autoatarraxante puxam **entre as camadas** (FM-01, FM-02). Somam-se a vibração contínua da ventoinha (FM-12) e a fluência do PETG morno (FM-03, S09).
- **Evidência:** decisão 12; `05` classe E1 já pergunta isso; decisão S1, "riscos restantes".
- **Premissas:** a resistência entre camadas do material real é UNKNOWN; a temperatura interna é UNKNOWN (B-02).
- **Correção:** manter a opção C (anel de aperto com insertos de latão e parafuso de máquina) como plano principal, e não como reserva, caso o cupom não chegue a tempo. Ou testar no G2 o ressalto na orientação final, com torque, arrancamento e um período de vibração.
- **Verificação:** cupom na orientação final, aperto e reaperto 5 vezes, e inspeção depois de rodar com a ventoinha.
- **Status:** PENDENTE (cupom G2).

### B-02 · MAJOR · O teste térmico está marcado depois da decisão que ele deveria informar
- **Componente:** escolha entre PETG e ASA, colunas dos insertos, ressaltos da ventoinha, HD da baia.
- **Problema:** a temperatura interna é UNKNOWN (decisão S1). O único teste térmico do plano é o *thermal soak* do portão **"Ready to install"** (`01` §7), que vem **depois** da impressão. Mas o material depende dessa temperatura, e o HD passou a exigir a ventoinha (decisão 19). O HDT do PETG de referência é de 68 °C (S13); o do ASA, de ≈ 86–96 °C conforme a marca (S14).
- **Por que importa:** se a caixa imprimir em PETG e a parte interna esquentar, os ressaltos e as colunas sob carga deformam (FM-03), e o reparo exige reimprimir.
- **Correção:**
  1. teste térmico de bancada **antes** de escolher o material: a placa rodando 24 h com carga, numa maquete (papelão ou caixa provisória) com a mesma área de entrada e de saída de ar e a ventoinha, com termopares no ar de saída, perto da placa de cobre e no HD;
  2. uma conta inicial: ΔT_ar ≈ P / (ρ · c_p · Q), que pede a potência real (UNKNOWN; medidor de tomada) e a vazão da ventoinha (ficha do FA09025L12LPB, sem o efeito da perda de carga).
- **Verificação:** curva de temperatura registrada; material escolhido com margem sobre o HDT.
- **Status:** ABERTO.

### C-02 · MAJOR · "Cabe em 220 × 220" vale sem brim e talvez só para PETG
- **Componente:** base e tampa principais, de 208,25 × 165 (decisão 20).
- **Problema:**
  - numa mesa de 220 mm sobram ≈ 5,9 mm por lado;
  - guias de fabricantes sugerem brim de 8–10 mm para ASA e ABS (S12, fonte de fabricante);
  - com uma margem de 8 mm, o envelope **não cabe** (`mesh_audit.py --bed 220x220x250 --margin 8` sai com código 2);
  - ASA em peça grande e plana também pede câmara fechada (FM-07).
- **Premissas:** o fornecedor e a impressora são UNKNOWN; os valores de brim são de fabricante, não de norma.
- **Correção:** registrar como requisito "impressora do fornecedor com mesa ≥ 256 mm **ou** PETG", e perguntar ao fornecedor o brim e a câmara para o material escolhido.
- **Verificação:** fatiamento do STL real, com o perfil do fornecedor.
- **Status:** ABERTO.

### D-01 · MAJOR · Tirar o módulo obriga a mexer no conector do botão Power
- **Componente:** módulo frontal em peça única, preso só na base (decisão 20), e a ligação do botão até o FP (decisão 6, ZIF de 10 vias e 0,5 mm).
- **Problema:**
  - o botão Power do plano A fica no painel do módulo, e o fio dele vai até o FP, na traseira, perto do HDMI (`00` §5.4);
  - nenhum documento prevê um **ponto de desconexão na emenda**;
  - tirar o módulo para manutenção obrigaria a soltar o flat no ZIF do FP, o único jeito conhecido de ligar a placa (FM-09, FM-10).
- **Correção:**
  - prender a plaquinha adaptadora FFC → 2,54 mm junto ao FP, para que o flat nunca seja manuseado;
  - colocar um par de conectores de 2 vias (Dupont, que o usuário já tem) na emenda do módulo;
  - fazer o mesmo para o cabo USB-C do hub e para os fios do alto-falante, se cruzarem a emenda.
- **Verificação:** tabela de sequência de montagem e manutenção (`domains.md` D), ensaiada a seco.
- **Status:** ABERTO.

### D-02 · MAJOR · O requisito de segurança contra fogo não está definido
- **Componente:** material da caixa (PETG ou ASA) e o equipamento ligado 24 h sem supervisão, numa escola.
- **Problema:**
  - a inflamabilidade só aparece no contexto da bateria (`06` HW-3: "PETG e ASA não são antichama");
  - PETG e ASA comuns costumam ser UL 94 HB ou sem classificação (S13, S14); existem versões antichama, como o PETG V0 (S13);
  - a IEC 62368-1 define requisitos por classe de fonte de energia (S17), e a classe deste conjunto (carregador externo de 12 V e 30 W, placa, HD) não foi avaliada.
- **Por que importa:** é segurança, não aparência. A decisão cabe ao usuário e à escola, mas precisa ser **tomada e registrada**.
- **Premissas:** isto **não** é falha confirmada: é um requisito ausente. Não afirmamos conformidade nem não conformidade com a norma.
- **Correção:**
  1. registrar o requisito: aceitar o risco por escrito, **ou** usar material antichama (por exemplo PETG V0), ou PETG/ASA com fontes de ignição afastadas e o carregador por fora;
  2. olhar a etiqueta do carregador para marcações de fonte limitada (LPS);
  3. se a escola exigir, consultar quem conheça a IEC 62368-1 (edição atual).
- **Verificação:** decisão registrada no `00`/`06`; ficha do material com a classe UL 94.
- **Status:** ABERTO (BLOCKED para a parte de classificação normativa).

### D-03 · MINOR · O acesso aos parafusos das abas da emenda não está desenhado
- **Componente:** 3 abas no piso e 2 nas laterais (decisão 20).
- **Problema:** não está escrito de onde entram os parafusos dessas abas, nem se a chave alcança depois que a placa estiver montada.
- **Correção:** sequência de montagem em tabela na fase 2.
- **Verificação:** a mesma tabela, conferida no CAD.
- **Status:** PENDENTE (fase 2).

### F-01 · MINOR · A lista de compras não acompanhou a decisão 20
- **Problema:**
  - o `buy_list.md` (B28) prevê "**4** parafusos M3 + **4** insertos" só para a tampa;
  - a decisão 20 acrescenta 5 uniões com M3 em insertos (3 no piso e 2 nas laterais);
  - a contagem não foi atualizada (FM-16).
- **Correção:** atualizar a quantidade, com reserva.
- **Verificação:** contagem de fixadores do CAD contra a lista de compras.
- **Status:** ABERTO.

### F-02 · MINOR · Tamanho antigo do conceito sem o contexto
- **Problema:** a decisão 18 ainda diz "Caixa ≈ 220 × 165 mm no conceito", e com a baia o plano A tem ≈ 266 × 165 (decisões 19 e 20). O texto é histórico, mas parece atual.
- **Correção:** acrescentar "(sem a baia do HD)".
- **Status:** ABERTO.

### F-03 · MINOR · Contradição interna no `02` (ver C-01)
- **Problema:** o §4.3 adota a classe c sem cupom; o §5.7 orça com a classe m.
- **Correção:** junto com a C-01.
- **Status:** ABERTO.

### E-01 · OBSERVAÇÃO · Forma depois das correções da sessão 10
- **Conferido no conceito 3D:** a frente está limpa; as emendas aparecem só onde existem, como junta de sombra; o módulo é uma peça só; a casca é contínua.
- **Observação:** a junta de sombra do topo, entre a tampa principal e o módulo, depende de as duas alturas casarem dentro da tolerância de Z das duas peças; conferir no CAD.
- **Status:** OBSERVAÇÃO.

## 4. Conferido sem achados (evidência)

- **Referencial:** o registro é canhoto, e a regra Y_cad = −Y está documentada (`03` §2.3), com a conferência sem espelhamento registrada na importação para o Fusion (`00` §8.2; documentado, não verificado aqui).
- **Rastreabilidade das medidas:** há vocabulário de status, protocolo de parar e perguntar, leitura do visor ampliado e inspeção do contato dos bicos (CLAUDE.md, registro). Prática acima da média.
- **Suporte do SSD:** ajustável, com arruelas e rasgo (`02` §5.6), coerente com a incerteza.
- **Empeno da placa:** substituído pelo teste da tira de papel e por apoios flutuantes (decisão 13).
- **Snap-fit:** a decisão S1 separa retenção (parafusos), alinhamento (lábio) e posicionamento (travas opcionais), proíbe viga em Z e tem um plano sem cupom (opção C). Raciocínio correto quanto à anisotropia (FM-01, FM-04).
- **Baia do HD:** desenhada pela norma SFF-8201, pelos furos laterais obrigatórios, com reserva para o adaptador e a ventoinha obrigatória.
- **Divisão em peças:** cada uma das 3 peças tem um motivo escrito (mesa de impressão; acesso à placa). O erro anterior (módulo dividido sem motivo) foi corrigido e catalogado.

## 5. Não conferido, e por quê

- **Domínio A inteiro:** não há CAD da caixa.
- **Alturas dos apoios e da tampa:** Z2 e Z4 estão PENDENTES no registro (BLOCKED).
- **Ligação do botão Power:** BT5 ou BT2 PENDENTE (BLOCKED).
- **Módulo frontal:** as medidas dos periféricos (PER1–PER10) não existem; os tamanhos do conceito são ilustrativos.
- **Profundidade das aberturas da parede grossa contra o metal dos plugues:** PER9 pendente.
- **Arquivo `cad/n1110_placa.dxf`:** não aberto nesta auditoria.

## 6. Testes físicos necessários antes de liberar a impressão final

| Teste | O que prova | Fecha | Quando |
|---|---|---|---|
| Térmico de bancada em maquete | Temperatura interna, necessidade da ventoinha, margem do material | B-02, parte da B-01 | **Antes** de escolher o material |
| Cupom G2 com uma feature longa | Escala e tolerância reais do fornecedor; encaixe do lábio | C-01, F-03 | Antes da peça final |
| Cupom G2: ressalto da ventoinha e coluna do inserto na orientação final | Torque, arrancamento, vibração | B-01 | Antes da peça final |
| Fatiamento com o perfil do fornecedor | Peças na mesa, com brim e câmara | C-02 | Ao pedir o orçamento |
| Sequência de montagem e manutenção a seco | Acesso e pontos de desconexão | D-01, D-03 | Com a primeira peça |

## 7. Perguntas ao usuário

1. **Segurança contra fogo (D-02):** a escola exige alguma coisa? Aceita PETG ou ASA comum com o risco registrado, ou prefere um material antichama?
2. **Fornecedor (C-02):** já há candidato? Qual impressora e qual material ele oferece? Ele imprime um cupom com uma peça longa?

---

## Avaliação da skill neste teste (para o relatório de validação)

| Alvo do teste de integração | Detectado? | Onde |
|---|---|---|
| Medidas ausentes ou não confiáveis | Sim | §5 (Z2, Z4, BT5/BT2, PER) |
| Referência de coordenadas | Sim (conferido, sem achado) | §4 |
| Soma de tolerâncias | Sim, achado novo, com números | C-01, F-03 |
| Colunas de fixação fracas | Sim | B-01, D-03 |
| Orientação de impressão e separação entre camadas | Sim | B-01, C-02 |
| Fluência e pré-carga | Sim | B-01, B-02 |
| Térmica e fluxo de ar | Sim, achado novo (ordem do teste) | B-02 |
| Conflitos de montagem e manutenção | Sim, achado novo | D-01, D-03 |
| Acesso aos conectores | Parcial (PER9 pendente no próprio projeto) | §5, D-01 |
| Divisões desnecessárias e transições visuais | Sim (conferido; erro anterior já corrigido) | E-01, §4 |
| Inconsistências de documentação | Sim, achados novos | F-01, F-02, F-03 |
| Segurança (fogo), fora da lista do pedido | Sim, achado novo | D-02 |
