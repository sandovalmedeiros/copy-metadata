# Onboarding: Copiador de Metadados GeoNetwork (MVP)

> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Público: humano testando a feature pela primeira vez

## 1. Preparar um lote de teste (5 minutos)

Abra o PowerShell na pasta do projeto e crie uma exportação falsa com 3 pastas UUID:

```powershell
$base = "$env:TEMP\IDEBAHIA-TESTE-20260923"
New-Item -ItemType Directory -Force "$base" | Out-Null
$uuids = "0b8733a3-93ba-4d18-aa6a-a63782546898", "11111111-2222-3333-4444-555555555555", "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
foreach ($u in $uuids) {
    New-Item -ItemType Directory -Force "$base\$u\metadata" | Out-Null
    Set-Content -Path "$base\$u\metadata\metadata.xml" -Value "<metadata>teste $u</metadata>" -Encoding utf8
}
# uma pasta SEM o arquivo-alvo, para testar o relatório de exceções:
New-Item -ItemType Directory -Force "$base\ffffffff-0000-0000-0000-000000000000" | Out-Null
$base
```

Anote o path impresso na última linha — é a sua **origem** de teste.

## 2. Executar o aplicativo

1. Rode o app (via Python: `python -m app.main` na raiz do projeto; ou o `.exe` empacotado, se já gerado)
2. A janela abre com três seletores vazios e o botão **Executar** desabilitado
3. Clique em **Procurar** ao lado de *Origem* e escolha a pasta de teste criada no passo 1
4. Clique em **Procurar** ao lado de *Arquivo-alvo* e navegue até `<uuid>\metadata\metadata.xml` de qualquer uma das pastas — o filtro já mostra só `.xml`
5. Clique em **Procurar** ao lado de *Destino* e escolha/crie uma pasta vazia (ex.: `%TEMP%\saida-teste`)
6. **Executar** habilita. Clique e acompanhe a barra de progresso (N de M pastas)

## 3. Conferir o esperado

- [ ] O destino contém **3 arquivos** `<uuid>.xml` (um por pasta COM alvo)
- [ ] O nome de cada arquivo é o UUID da pasta de origem, não "metadata.xml"
- [ ] O conteúdo de cada arquivo bate com o original (abra e compare)
- [ ] O relatório mostra: 3 copiados, **1 alvo ausente** (a pasta `ffffffff-...`), 0 erros
- [ ] A pasta sem alvo não impediu as demais

## 4. Testes de exceção (mais 5 minutos)

1. **Sobrescrita**: execute de novo sobre o mesmo destino → o app deve apresentar a escolha (sobrescrever / pular) e registrar as ocorrências no relatório
2. **Cancelamento**: crie um lote maior (copie/cole as pastas UUID 20×) e cancele no meio → a janela responde, as cópias feitas permanecem, o relatório parcial aparece
3. **Origem inválida**: aponte a origem para um path inexistente → mensagem clara na validação, nada copiado, app continua utilizável

## 5. O que NÃO é bug

- Arquivo sem a extensão `.xml` no diálogo de seleção (o filtro é proposital — a demanda é sobre `.xml`)
- O app não abre nem valida o conteúdo do XML — cópia e renomeação apenas
- O app não importa nada no GeoNetwork — preparar os arquivos é o escopo

## 6. Achou um problema?

Registre com `/reversa-debugger` (registro e triagem) ou, se for defeito pequeno com consenso de correção imediata, `/reversa-debugger-fix`. Não edite o código diretamente sem registrar.
