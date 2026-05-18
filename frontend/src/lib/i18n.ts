export type Lang = 'en' | 'pt';

export const TRANSLATIONS = {
  en: {
    // Navigation
    nav_receivables: 'Receivables',
    nav_config: 'Config',
    nav_soon: 'soon',
    // Dashboard
    page_title: 'Operator panel',
    page_subtitle: 'Review receivables, simulate pricing and settle outstanding balances.',
    btn_refresh: 'Refresh',
    btn_refreshing: 'Refreshing…',
    // KPI
    kpi_total: 'Total',
    kpi_pending: 'Pending',
    kpi_settled: 'Settled',
    kpi_cancelled: 'Cancelled',
    // Pricing simulator
    sim_title: 'Pricing simulator',
    sim_subtitle: 'Computes present value, settlement value and applied rate without persisting.',
    sim_product_code: 'Product code',
    sim_currency: 'Currency',
    sim_face_value: 'Face value',
    sim_issue_date: 'Issue date',
    sim_due_date: 'Due date',
    sim_btn_simulate: 'Simulate',
    sim_btn_simulating: 'Simulating…',
    sim_present_value: 'Present value',
    sim_settlement_value: 'Settlement value',
    sim_eff_rate: 'Effective rate / month',
    sim_base_rate: 'Base rate / month',
    sim_spread: 'Spread / month',
    sim_term: 'Term (months)',
    sim_fx: 'FX applied',
    // Filters
    filter_assignor: 'Assignor (document)',
    filter_assignor_placeholder: 'Only digits',
    filter_product: 'Product',
    filter_currency: 'Currency',
    filter_status: 'Status',
    filter_status_any: 'Any',
    filter_reset: 'Reset',
    // Table
    col_reference: 'Reference',
    col_assignor: 'Assignor',
    col_product: 'Product',
    col_face_value: 'Face value',
    col_issue: 'Issue',
    col_due: 'Due',
    col_status: 'Status',
    btn_settle: 'Settle',
    btn_settling: 'Settling…',
    btn_cancel: 'Cancel',
    no_receivables: 'No receivables match the current filters.',
    loading_receivables: 'Loading receivables…',
    showing_x_of_y: 'Showing {shown} of {total} receivables.',
    // Status badge
    status_pending: 'Pending',
    status_settled: 'Settled',
    status_cancelled: 'Cancelled',
    // Help modal
    help_btn: 'Help',
    help_title: 'How to use Credit Engine',
    help_kpi_title: 'KPI Cards',
    help_kpi_body:
      'Shows the real-time count of receivables by status (Pending, Settled, Cancelled). The bar inside each card shows the proportional share.',
    help_sim_title: 'Pricing Simulator',
    help_sim_body:
      'Calculates present value and settlement value for a receivable without saving to the database. Enter the product code, face value, currency and dates, then click Simulate.',
    help_filters_title: 'Filters',
    help_filters_body:
      'Filter receivables by assignor document (CPF/CNPJ digits only), product code, currency or status. Click Reset to clear all filters.',
    help_table_title: 'Receivables Table',
    help_table_body:
      'Lists all receivables matching the current filters. For PENDING receivables, Settle creates a settlement locking the value, and Cancel voids the receivable.',
    help_close: 'Close',
  },
  pt: {
    // Navegação
    nav_receivables: 'Recebíveis',
    nav_config: 'Configurações',
    nav_soon: 'em breve',
    // Dashboard
    page_title: 'Painel do operador',
    page_subtitle: 'Revise recebíveis, simule precificação e liquide saldos pendentes.',
    btn_refresh: 'Atualizar',
    btn_refreshing: 'Atualizando…',
    // KPI
    kpi_total: 'Total',
    kpi_pending: 'Pendente',
    kpi_settled: 'Liquidado',
    kpi_cancelled: 'Cancelado',
    // Simulador
    sim_title: 'Simulador de precificação',
    sim_subtitle: 'Calcula valor presente, valor de liquidação e taxa aplicada sem persistir.',
    sim_product_code: 'Código do produto',
    sim_currency: 'Moeda',
    sim_face_value: 'Valor de face',
    sim_issue_date: 'Data de emissão',
    sim_due_date: 'Data de vencimento',
    sim_btn_simulate: 'Simular',
    sim_btn_simulating: 'Simulando…',
    sim_present_value: 'Valor presente',
    sim_settlement_value: 'Valor de liquidação',
    sim_eff_rate: 'Taxa efetiva / mês',
    sim_base_rate: 'Taxa base / mês',
    sim_spread: 'Spread / mês',
    sim_term: 'Prazo (meses)',
    sim_fx: 'FX aplicado',
    // Filtros
    filter_assignor: 'Cedente (documento)',
    filter_assignor_placeholder: 'Somente dígitos',
    filter_product: 'Produto',
    filter_currency: 'Moeda',
    filter_status: 'Status',
    filter_status_any: 'Todos',
    filter_reset: 'Limpar',
    // Tabela
    col_reference: 'Referência',
    col_assignor: 'Cedente',
    col_product: 'Produto',
    col_face_value: 'Valor de face',
    col_issue: 'Emissão',
    col_due: 'Vencimento',
    col_status: 'Status',
    btn_settle: 'Liquidar',
    btn_settling: 'Liquidando…',
    btn_cancel: 'Cancelar',
    no_receivables: 'Nenhum recebível encontra os filtros atuais.',
    loading_receivables: 'Carregando recebíveis…',
    showing_x_of_y: 'Exibindo {shown} de {total} recebíveis.',
    // Badge de status
    status_pending: 'Pendente',
    status_settled: 'Liquidado',
    status_cancelled: 'Cancelado',
    // Modal de ajuda
    help_btn: 'Ajuda',
    help_title: 'Como usar o Credit Engine',
    help_kpi_title: 'Cards de KPI',
    help_kpi_body:
      'Exibe a contagem em tempo real de recebíveis por status (Pendente, Liquidado, Cancelado). A barra dentro de cada card mostra a proporção em relação ao total.',
    help_sim_title: 'Simulador de Precificação',
    help_sim_body:
      'Calcula o valor presente e o valor de liquidação de um recebível sem salvar no banco de dados. Informe o código do produto, valor de face, moeda e datas, depois clique em Simular.',
    help_filters_title: 'Filtros',
    help_filters_body:
      'Filtre recebíveis por documento do cedente (somente dígitos do CPF/CNPJ), código do produto, moeda ou status. Clique em Limpar para resetar todos os filtros.',
    help_table_title: 'Tabela de Recebíveis',
    help_table_body:
      'Lista todos os recebíveis que correspondem aos filtros atuais. Para recebíveis PENDENTES, Liquidar cria uma liquidação travando o valor, e Cancelar anula o recebível.',
    help_close: 'Fechar',
  },
} as const;

export type TranslationKey = keyof typeof TRANSLATIONS.en;
