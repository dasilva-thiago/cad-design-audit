# Relatório de validação — skill `cad-design-audit` — 18/11/2026

## 0. O que foi testado, e com que limite

| Tipo de teste | O que é | Grau de evidência |
|---|---|---|
| **Scripts** (`mesh_audit.py`, `stack_up.py`) | 18 testes automáticos com arquivos sintéticos de resposta conhecida | **Execução real**: `python -m unittest discover -s tests` → 18 OK |
| **Cenários 1–8** | Casos sintéticos descritos em texto (e, no cenário 1, também em malha), auditados seguindo o `SKILL.md` | **Simulação.** Quem escreveu a skill também a aplicou, o que é um viés: o teste mostra que a skill cobre os mecanismos, não que outro agente chegaria às mesmas conclusões. Nenhuma peça física foi impressa |
| **Integração eduServer Box** | Auditoria completa sobre os artefatos reais do repositório (`eduserver_box_integration_audit.md`) | **Artefatos reais**, mas **sem CAD da caixa** (ainda não existe): o domínio A não pôde ser exercitado em geometria real |

Para cada caso, os critérios avaliados foram:
- **C1** identifica o problema;
- **C2** explica o mecanismo;
- **C3** usa evidência adequada;
- **C4** não traz número sem fonte;
- **C5** separa incerteza de falha confirmada;
- **C6** dá a severidade adequada;
- **C7** propõe uma correção prática;
- **C8** define como verificar a correção.

---

## 1. Testes dos scripts (execução real)

| Teste | Esperado | Resultado |
|---|---|---|
| Cubo fechado (STL binário e ASCII) | Estanque, volume exato, 1 componente, código 0 | OK |
| Caixa aberta (1 face a menos) | 4 arestas de borda, código 1 | OK |
| Uma face invertida | 3 arestas com orientação inconsistente | OK |
| Todas as normais invertidas | Volume negativo, erro "inverted" | OK |
| Dois cubos dividindo uma aresta | 1 aresta não-manifold | OK |
| Face duplicada | 1 duplicada | OK |
| 3MF em centímetros | Unidade convertida (10 × 20 × 30 mm) | OK |
| Mesa: 208,25 × 165 numa de 220 com margem de 5 e de 8 | Cabe com 5; não cabe com 8 (código 2) | OK |
| Peça que só cabe girada 90° | `fits_rotated_90` | OK |
| Arquivo ilegível | Código 3 | OK |
| Mesa escrita como nome de impressora (não aceito) | Código 3, pede WxDxH | OK |
| **Espessura de parede** (caixa oca com paredes de 1 e 2 mm) | Mínimo de 1,000; `--min-wall 1.2` acusa | OK (função acrescentada depois do cenário 1) |
| Espessura em malha aberta | Pula, com aviso | OK |
| Soma de tolerâncias: pior caso e RSS independentes | Valores analíticos | OK |
| Grupo correlacionado somado linearmente | RSS = soma do grupo | OK |
| Tolerância assimétrica | Limites corretos | OK |
| Contribuinte sem fonte | Aviso | OK |

---

## 2. Cenários sintéticos

### Cenário 1 — Caixa simples com parede fina demais
**Entrada:** caixa de PETG em FDM, 120 × 80 × 40 mm, paredes de 2 mm, exceto a lateral do conector, afinada para 0,8 mm para o plugue USB passar. Material e fornecedor sem ficha. Também foi gerada uma malha sintética (caixa oca com paredes de 1 e 2 mm) para exercitar a ferramenta.

**Saída da skill:**
- **A-01 MAJOR.** Parede de 0,8 mm na lateral do conector, achada pela varredura de espessura (`--thickness`) na malha sintética e pela leitura da especificação.
  - *Mecanismo:* a parede fica abaixo do que normalmente se imprime com segurança com bico de 0,4 mm, e é justamente a parede que recebe a força de inserção do plugue.
  - *Evidência:* o mínimo da varredura e a especificação.
  - *Incerteza:* o mínimo do processo **não foi inventado**; a skill pede a ficha do fornecedor e marca o limite como PENDING.
  - *Correção:* recuar o conector ou engrossar a parede localmente com um recesso; reforço no lado de dentro.
  - *Verificação:* nova varredura e o cupom.

**Fraqueza encontrada:** a primeira versão do `mesh_audit.py` não media espessura e só podia dizer "confira no CAD". **Melhoria:** acrescentada a varredura aproximada por raio (`--thickness`, `--min-wall`), com testes. Ela continua sendo um localizador; a confirmação vai para o CAD.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ (malha sintética + especificação) | ✓ (limite pedido ao fornecedor) | ✓ | ✓ | ✓ | ✓ |

### Cenário 2 — Ressalto de parafuso com risco de rachar ou arrancar
**Entrada:** inserto de latão M3 num ressalto de Ø 5 mm com furo de 4,0 mm (parede de 0,5 mm), ressalto solto do meio do piso, sem nervuras, eixo em Z, tampa apertada 4 vezes por ano. A ficha do inserto não foi fornecida.

**Saída:**
- **B-01 MAJOR (FM-02, FM-01).** A parede de 0,5 mm em volta do inserto racha na instalação a quente ou no aperto. O arrancamento puxa entre camadas, porque o eixo está em Z. O ressalto solto flexiona.
  - A skill **não** cita um número de "parede mínima" sem fonte: pede a ficha do inserto (furo e parede recomendados) e marca PENDING.
  - *Correções:* ligar o ressalto às paredes ou a nervuras, aumentar o diâmetro conforme a ficha, ou usar porca cativa.
  - *Verificação:* cupom com o inserto real, torque e arrancamento, e 4 ciclos de abre e fecha.
- **B-02 MINOR.** Fluência sob o aperto (FM-03): conferir se a cabeça do parafuso apoia no inserto (metal com metal) ou no plástico.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ (a ficha é exigida) | ✓ | ✓ | ✓ | ✓ | ✓ |

### Cenário 3 — Snap-fit numa orientação ruim
**Entrada:** gancho em viga de 1,5 mm de espessura, 10 mm de comprimento e 1 mm de flecha, na parede de uma tampa impressa em pé (a viga dobra entre camadas), em PETG.

**Saída:**
- **B-03 MAJOR (FM-04, FM-01).**
  - *Conta de triagem:* ε ≈ 1,5 · h · y / l² = 1,5 · 1,5 · 1 / 100 = **2,25 %** (S03).
  - A deformação admissível do PETG **entre camadas** é UNKNOWN: a skill não usa os exemplos do guia da Bayer como limite e marca o achado como PENDING até o cupom.
  - *Mecanismo:* a flexão traciona a união entre camadas, a direção mais fraca.
  - *Correções:* deitar a viga no plano de impressão, transformar o gancho em peça separada impressa deitada, ou trocar a retenção por parafuso e deixar o gancho só para posicionar.
  - *Verificação:* cupom na orientação final, 10 ciclos.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ (a conta é de triagem e está marcada como tal) | ✓ | ✓ | ✓ | ✓ |

### Cenário 4 — Peça válida mas impossível de montar
**Entrada:** caixa com placa presa por 4 parafusos por cima. A tampa tem uma divisória interna que, fechada, fica sobre 2 desses parafusos. O conector de alimentação é soldado à placa e passa por um furo redondo justo na parede, menor que a capa do plugue. A geometria final não tem interferência.

**Saída:**
- **D-01 BLOCKER (FM-09).** A tabela de sequência mostra que a placa não entra: o conector precisa atravessar a parede, mas a placa desce na vertical, e o furo não deixa o conector entrar de lado. A geometria final é válida, mas não existe sequência de montagem que chegue nela.
  - *Correção:* abrir o furo como rasgo até a borda da parede, ou dividir a parede nesse ponto.
  - *Verificação:* sequência passo a passo no CAD, com movimento.
- **D-02 MAJOR.** Os 2 parafusos sob a divisória não têm acesso de chave enquanto a tampa está fechada. Só é possível montar antes da tampa, mas a manutenção da placa exige abrir a tampa e soltá-los: conferir.
- **D-03 MAJOR (FM-10).** A capa do plugue é maior que o furo.

**Fraqueza encontrada:** não havia um formato para a sequência de montagem. **Melhoria:** acrescentada a tabela "passo / peça / fixador e ferramenta / acesso / o que bloqueia depois" em `domains.md` D, também para a manutenção.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Cenário 5 — Soma de tolerâncias que falha no pior caso
**Entrada:** lábio de encaixe numa peça de ≈ 200 mm, com folga de 0,35 por lado orçada com a tolerância de feature de 0,5–3 mm. É o caso **real** do eduServer (C-01 do teste de integração).

**Saída:**
- **C-01 MAJOR (FM-05).** `stack_up.py`:
  - como orçado, pior caso de +0,15;
  - com a tolerância do contorno (ISO 2768-m, 120–400 mm), pior caso de −0,30;
  - na premissa sem cupom (classe c), −1,70.
- A skill explica a **correlação** do erro de escala (mesma impressora), mostra que ela pode salvar o encaixe mas não está quantificada, e não aceita o RSS para peça única.
- *Correção:* centragem em poucos pontos curtos, ou um cupom com uma feature longa.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ (conta reproduzível, fonte da norma marcada como secundária) | ✓ | ✓ | ✓ | ✓ | ✓ |

### Cenário 6 — Caixa eletrônica mal ventilada
**Entrada:** computador de placa única de ~15 W numa caixa fechada de 100 × 80 × 30 mm, com ventoinha de 30 mm soprando para fora e 4 furos de 3 mm logo ao lado dela. Sem dado de temperatura.

**Saída:**
- **D-04 MAJOR (FM-11).**
  - Entrada e saída estão lado a lado: a ventoinha recircula o próprio ar.
  - A área de entrada (4 furos de Ø 3 ≈ 28 mm²) é muito menor que a área da ventoinha. A regra prática de "≥ 1,5 × a área da ventoinha" é apresentada como **regra de fabricante** (S16), só para mostrar o tamanho do desvio.
  - A temperatura é UNKNOWN; a skill **não** afirma que vai superaquecer.
  - *Correção:* entrada do lado oposto e embaixo, saída em cima ou perto da fonte de calor, e área de entrada maior.
  - *Verificação:* teste de aquecimento com termopar em carga máxima.

**Fraqueza encontrada:** faltava uma estimativa física simples. **Melhoria:** acrescentada em `methods.md` a conta ΔT_ar ≈ P / (ρ · c_p · Q), com o aviso de que a vazão de catálogo é ao ar livre (o limite é otimista) e de que ela não dá os pontos quentes.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ (a regra prática está rotulada como tal) | ✓ | ✓ | ✓ | ✓ |

### Cenário 7 — Medidas do CAD e da documentação que não batem
**Entrada:**
- o desenho diz furo Ø 3,2 para M3;
- o parâmetro do CAD diz `hole_d = 3.0`;
- a lista de materiais pede parafusos M2,5;
- a nota de montagem diz "4 parafusos", e o CAD tem 6 furos.

**Saída:**
- **F-01 MAJOR:** M2,5 contra M3 compra o fixador errado.
- **F-02 MINOR:** 3,0 contra 3,2: qual vale? Para impressão, o furo sai menor (FM-06), então o 3,0 do CAD pode não passar um M3. Pede o cupom.
- **F-03 MINOR:** 4 contra 6 parafusos.
- A skill **não escolhe** qual documento está certo: lista os dois lados de cada conflito e pergunta.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Cenário 8 — Divisão desnecessária em peças e incoerência visual
**Entrada:** gabinete pequeno (150 × 150 mm, cabe na mesa) dividido em 4 peças. Uma emenda atravessa o painel frontal, no meio do visor. Há uma faixa decorativa escura em volta. O módulo frontal tem base e tampa sem nada que precise de acesso por cima.

**Saída:**
- **E-01 MAJOR (FM-15).** Divisões sem motivo: a peça cabe inteira na mesa, e a tampa do módulo não dá acesso a nada. Elas acrescentam emenda, fixadores e tolerância.
  - *Correção:* uma peça só, ou dividir só onde houver motivo escrito.
- **E-02 MAJOR.** A emenda passa pela face principal (o visor), e a faixa decorativa não corresponde a nenhuma emenda.
  - *Correção:* face principal limpa, e as emendas reais como junta de sombra discreta.
- **E-03 OBSERVAÇÃO.** A skill separa o que é preferência estética do que é requisito: a faixa não é uma falha de engenharia, mas uma linha sem motivo.

Este cenário reproduz três erros reais da sessão 10 do eduServer, achados pelo usuário e não pelo agente. A classe FM-15 e a regra "toda linha e toda divisão com motivo escrito" vieram deles.

| C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (estética separada de engenharia) | ✓ | ✓ |

---

## 3. Integração eduServer Box (artefatos reais)

Relatório completo em `eduserver_box_integration_audit.md`:
- **10 achados:** 6 MAJOR, 3 MINOR e 1 OBSERVAÇÃO, além de 3 itens BLOCKED por dados que o projeto já sabe que faltam;
- **achados novos** que os documentos do projeto não registravam:
  - o lábio não fecha no pior caso (C-01);
  - o teste térmico está depois da decisão do material (B-02);
  - "cabe em 220" vale sem brim (C-02);
  - não há ponto de desconexão do botão Power na emenda do módulo (D-01);
  - o requisito de fogo não está definido (D-02);
  - a lista de compras e o tamanho estão desatualizados (F-01, F-02).
- **Limite:** sem CAD da caixa, o domínio A não foi exercitado em geometria real. Quando houver CAD, a próxima validação deve rodar `mesh_audit.py` nos STL de cada peça e a interferência do Fusion na montagem.

---

## 4. Fraquezas da skill e o que foi melhorado

| Fraqueza | Onde apareceu | Correção |
|---|---|---|
| Sem medição de espessura de parede em malha | Cenário 1 | `mesh_audit.py --thickness/--min-wall`, com 2 testes |
| Sem formato para a sequência de montagem | Cenário 4 | Tabela de montagem e manutenção em `domains.md` D |
| Sem estimativa física de aquecimento do ar | Cenário 6 | ΔT_ar ≈ P / (ρ · c_p · Q) em `methods.md` §5, com limites |
| "Cabe na mesa" sem brim | Integração | Margem por lado explícita no `mesh_audit.py`; FM-08 e domínio C pedem o brim do material |
| Validação feita pelo próprio autor | Todos os cenários | **Não corrigida.** Recomenda-se uma rodada de validação por outro agente ou revisor, sem contexto prévio |

## 5. Limites que continuam

- **Precisam de dados ou de teste físico:**
  - resistência entre camadas e limites de snap-fit para o material e a orientação reais;
  - arrancamento e torque de insertos;
  - fluência;
  - precisão de furo e escala do fornecedor;
  - empeno numa impressora específica;
  - comportamento térmico;
  - vibração;
  - encaixe de plugues reais;
  - comportamento ao fogo e conformidade normativa.
- **Precisam de ferramenta externa:**
  - interferência e distâncias entre peças (CAD; no Fusion, `analyzeInterference` e `measureMinimumDistance`);
  - validade de BRep e volume de interseção em STEP (ambiente OCP/CadQuery, não incluído);
  - balanços e suportes (fatiador).
- **Normas:** ISO 2768, ISO 14253-1, ISO/ASTM 52910, IEC 62368-1 e IPC/JEDEC-9704A foram consultadas pelo escopo e por fontes secundárias. Nenhuma cláusula foi reproduzida, e nenhuma conformidade é afirmada.
