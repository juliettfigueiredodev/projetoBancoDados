--Banco de Dados

DROP TABLE IF EXISTS pagamento CASCADE;
DROP TABLE IF EXISTS reserva CASCADE;
DROP TABLE IF EXISTS quarto_manutencao CASCADE;
DROP TABLE IF EXISTS quarto CASCADE;
DROP TABLE IF EXISTS hospede CASCADE;

create database if not exists sistema_hotel;

--use sistema_hotel;

-- Tabela Hospede
create table if not exists hospede (
	id SERIAL primary key,
	nome VARCHAR(100) not null,
	-- CHECK para verificar se o valor para tipo de documento está entre os listados
	tipo_documento VARCHAR(15) not null check (tipo_documento in ('CPF', 'PASSAPORTE')),
	valor_documento VARCHAR(14) not null,
	-- UNIQUE para evitar a repetição do valor no campo email
	email VARCHAR(150) not null unique ,
	telefone VARCHAR(20) not null
);

--Tabela Quarto
create table if not exists quarto(
	NUMERO INTEGER primary key not null,
	--CHECK para verificar se o valor está entre os listados
	tipo VARCHAR(10) not null check (tipo in ('SIMPLES', 'DUPLO', 'LUXO')),
	capacidade INTEGER not null ,
	--CHECK para verificar a comparação lógica
	tarifa_base_diaria DECIMAL(10,2) not null check (tarifa_base_diaria >=0),
	--CHECK para verificar se o valor está entre os listados
	status VARCHAR(30) not null check (status in ('DISPONIVEL', 'OCUPADO', 'MANUTENCAO', 'BLOQUEADO'))
);

--Tabela quartos em manutenção
create table if not exists quarto_manutencao(
	id SERIAL primary key,
	motivo TEXT not NULL,
	--DEFAULT para garantir que vai ter algum valor
	data_inicio DATE not null default CURRENT_DATE,
	data_fim_prevista DATE not null default CURRENT_DATE + interval '7 days',
	numero_quarto INTEGER not null,
	constraint fk_manutencao_quarto
		foreign key (numero_quarto)
		references quarto(NUMERO)
		--UPDATE CASCADE atualiza em cascata
		on update cascade
		-- DELETE RESTRICT deleta apenas se não tiver nada atrelado
		on delete restrict
);

--Tabela Reserva
create table if not exists reserva(
	--ATRIBUTOS
	id SERIAL primary key,
	--DEFAULT para garantir que vai ter algum valor
	data_entrada DATE not null default CURRENT_DATE,
	data_saida DATE not null,
	nro_hospedes INTEGER not null,
	--CHECK para verificar se o valor está entre os listados
	origem VARCHAR(10) not null check(origem in ('site', 'telefone', 'balcao')),
	
	-- VALIDAÇÃO CHECK: Saída após no mínimo uma noite
	constraint check_periodo_reserva check (data_saida > data_entrada),
	
	-- CHAVES ESTRANGEIRAS
	id_hospede INTEGER not null,
	numero_quarto INTEGER not null,
	
	-- REGRAS PARA GARANTIR INTEGRIDADE, CONSISTENCIA E QUALIDADE DOS DADOS
	constraint fk_reserva_hospede
		foreign key (id_hospede)
		references hospede (id)
		--UPDATE CASCADE atualiza em cascata
		on update cascade
		-- DELETE RESTRICT deleta apenas se não tiver nada atrelado
		on delete restrict,
	
	constraint fk_reserva_quarto
		foreign key (numero_quarto)
		references quarto (NUMERO)
		--UPDATE CASCADE atualiza em cascata
		on update cascade
		-- DELETE RESTRICT deleta apenas se não tiver nada atrelado
		on delete restrict
);


--Tabela Pagamento
create table if not exists pagamento (
	id SERIAL primary key,
	data DATE,
	--CHECK para verificar se o valor está entre os listados
	forma VARCHAR(10) not null check (forma in ('dinheiro', 'credito', 'debito', 'pix')),
	valor DECIMAL(8,2) not null,
	id_reserva INTEGER not null,
	constraint fk_pagamento_reserva
		foreign key (id_reserva)
		references reserva(id)
		--UPDATE CASCADE atualiza em cascata
		on update cascade
		-- DELETE RESTRICT deleta apenas se não tiver nada atrelado
		on delete restrict
);

-- ========================
-- ETAPA 3 - PROJETO FINAL
-- Carga de dados (INSERTs)
-- ========================

-- HOSPEDES COM CPF OU PASSAPORTE
insert into hospede (nome, tipo_documento, valor_documento, email, telefone) VALUES
('João Silva Santos', 'CPF', '123.456.789-00', 'joao.silva@email.com', '(88) 98765-4321'),
('Maria Oliveira Costa', 'CPF', '987.654.321-00', 'maria.oliveira@email.com', '(81) 99876-5432'),
('Robert Johnson', 'PASSAPORTE', 'US1234567', 'robert.j@email.com', '+1 555-0123'),
('Sophie Martin', 'PASSAPORTE', 'FR9876543', 'sophie.m@email.com', '+33 6 12 34 56 78'),
('Carlos Eduardo Lima', 'CPF', '456.789.123-00', 'carlos.lima@email.com', '(87) 97654-3210'),
('Ana Paula Souza', 'CPF', '321.654.987-00', 'ana.souza@email.com', '(88) 96543-2109');

insert into quarto (NUMERO, tipo, capacidade,tarifa_base_diaria, status) values
-- QUARTOS DISPONIVEIS
(101, 'SIMPLES', 1, 150.00, 'DISPONIVEL'),
(102, 'SIMPLES', 1, 150.00, 'DISPONIVEL'),
(201, 'DUPLO', 2, 250.00, 'DISPONIVEL'),
(202, 'DUPLO', 2, 250.00, 'DISPONIVEL'),
(303, 'LUXO', 4, 500.00, 'DISPONIVEL'),

--QUARTOS OCUPADOS
(103, 'SIMPLES', 1, 150.00, 'OCUPADO'),
(203, 'DUPLO', 2, 250.00, 'OCUPADO'),
(301, 'LUXO', 4, 500.00, 'OCUPADO'),

-- QUARTOS EM MANUTENCAO
(104, 'SIMPLES', 1, 150.00, 'MANUTENCAO'),
(204, 'DUPLO', 2, 250.00, 'MANUTENCAO'),

-- QUARTO BLOQUEADO
(302, 'LUXO', 4, 500.00, 'BLOQUEADO');

insert into quarto_manutencao (motivo, data_inicio, data_fim_prevista, numero_quarto) values
('Troca de ar-condicionado e pintura de paredes', '2026-02-01', '2026-02-05',104),
('Substituição completa de encanamento do banheiro e troca de revestimentos', '2026-02-03', '2026-02-10', 204);

insert into reserva (data_entrada, data_saida, nro_hospedes, origem,id_hospede, numero_quarto) values
--RESERVAS ATIVAS
('2026-02-27', '2026-03-05', 3, 'site', 4, 303),
('2026-02-05', '2026-02-10', 1, 'site',1, 103),
('2026-01-05', '2026-02-09', 2, 'telefone',2, 203),
('2026-01-20', '2026-02-14', 4, 'balcao', 3, 301);

insert into pagamento (data, forma, valor, id_reserva) values
('2026-02-05', 'credito', 750.00, 1),
('2026-01-05', 'pix', 500.00, 2),
('2026-02-05', 'pix', 500.00, 2),
('2026-01-20','debito',1000.00, 3),
('2026-02-04', 'credito', 4000.00, 3);

-- ========================
-- Consultas (SELECTs)
-- ========================

--Otimização para Consulta 1

-- Filtro principal (WHERE) — maior impacto
create index idx_reserva_data_saida on reserva(data_saida);

-- Cobre o ORDER BY junto com o filtro WHERE
create index idx_reserva_data_saida_entrada on reserva(data_saida, data_entrada);

-- JOINs
create index idx_reserva_id_hospede on reserva(id_hospede);
create index idx_reserva_numero_quarto on reserva(numero_quarto); 

--Consulta 1: listar todas as reservas ativas com informações do hóspede e quarto
--Mostra nome do hóspede, dados da reserva e tipo de quarto
explain analyze SELECT 
    r.id AS id_reserva,
    h.nome AS nome_hospede,
    h.email,
    h.telefone,
    q.NUMERO AS numero_quarto,
    q.tipo AS tipo_quarto,
    r.data_entrada,
    r.data_saida,
    r.nro_hospedes, 
    r.origem
FROM reserva AS r
INNER JOIN hospede AS h 
	ON r.id_hospede = h.id
INNER JOIN quarto AS q 
	ON r.numero_quarto = q.NUMERO
WHERE r.data_saida >= CURRENT_DATE
ORDER BY r.data_entrada;

-- Otimização para Consulta 2

-- JOIN pagamento --> reserva (maior impacto aqui)
create index idx_pagamento_id_reserva on pagamento (id_reserva);

-- Cobre o ORDER BY (evita filesort)
create index idx_pagamento_id_reserva_valor on pagamento (id_reserva, valor);

--Consulta 2: Valor total de pagamentos por reserva
--Calcula quanto cada reserva já pagou
explain analyze select
	r.id as id_reserva,
	h.nome as nome_hospede,
	q.NUMERO as numero_quarto,
	COUNT(p.id) as qtd_pagamentos,
	SUM(p.valor) as valor_total_pago,
	r.data_entrada,
	r.data_saida
from reserva as r
inner join hospede as h 
	on r.id_hospede = h.id
inner join quarto as q 
	on r.numero_quarto = q.NUMERO
inner join pagamento as p 
	on p.id_reserva = r.id 
group by r.id, h.nome, q.NUMERO, r.data_entrada, r.data_saida 
order by valor_total_pago desc;

--Consulta 3: Quartos com ou sem manutenção agendada (LEFT JOIN)
--Lista todos os quartos, mostrando quais estão em manutenção e quais não

select 
	q.NUMERO as numero_quarto, --apelido para aparecer na tabela de consulta
	q.tipo as tipo_quarto,
	q.status,
	q.tarifa_base_diaria,
	qm.motivo as motivo_manutencao,
	qm.data_inicio,
	qm.data_fim_prevista
from quarto as q --apelido para facilitar a codificação
left join quarto_manutencao as qm
		on q.NUMERO = qm.numero_quarto
order by q.NUMERO;

--Otimização para Consulta 4

create index idx_hospede_tipo_id on hospede (tipo_documento, id);

--Consulta 4: Filtrar hóspedes brasileiros com suas reservas ativas
explain analyze select 
	h.nome as nome_hospede,
	h.valor_documento as cpf,
	h.email,
	r.data_entrada,
	r.data_saida,
	q.NUMERO as numero_quarto,
	q.tipo as tipo_quarto
from hospede h 
inner join reserva r 
	on h.id = r.id_hospede
inner join quarto q 
	on r.numero_quarto = q.numero 
	where h.tipo_documento = 'CPF'
		and r.data_saida >= CURRENT_DATE
order by r.data_entrada;

--Consulta 5: Filtrar quartos disponíveis com tarifa abaixo de R$300
select
	NUMERO as numero_quarto,
	tipo as tipo_quarto,
	capacidade,
	tarifa_base_diaria,
	status
from quarto
	where status = 'DISPONIVEL'
	and tarifa_base_diaria < 300.00
order by tarifa_base_diaria;

-- ========================
-- ETAPA 4 - PROJETO FINAL
-- VIEWS, TRIGGERS E PROCEDURE
-- ========================

-- VIEW : vw_reservas_completas
-- Facilitar a consulta de reservas com todos os dados relevantes do hóspede, quarto 
-- e valor total pago. Evita repetir o JOIN em todo lugar do sistema. Útil para relatórios,
-- painéis e listagens do front-end.

create or replace view vw_reservas_completas as
	select
		r.id as id_reserva,
		h.nome as nome_hospede,
		h.tipo_documento,
		h.valor_documento,
		h.email,
		h.telefone,
		q.NUMERO as numero_quarto,
		q.tipo as tipo_quarto,
		q.tarifa_base_diaria,
		r.data_entrada,
		r.data_saida,
		(r.data_saida - r.data_entrada) as qtd_diarias,
		r.nro_hospedes,
		r.origem,
		coalesce(sum(p.valor), 0) as total_pago
	from reserva as r
	inner join hospede as h
		on r.id_hospede = h.id
	inner join quarto as q
		on r.numero_quarto = q.NUMERO
	left join pagamento as p
		on p.id_reserva = r.id
	group by
		r.id, h.nome, h.tipo_documento, h.valor_documento, h.email, h.telefone,
		q.NUMERO, q.tipo, q.tarifa_base_diaria, r.data_entrada, r.data_saida,
		r.nro_hospedes, r.origem;

-- select * from vw_reservas_completas where data_saida <= CURRENT_DATE;


-- ===================
-- VIEW MATERIALIZADA: mv_resumo_financeiro_quarto
-- Relatório financeiro agregado por quarto, mostrando receita total, quantidade
-- de reservas e ticket médio. Por ser materializada, o resultado fica armazenado
-- fisicamente (ideal para dashboards que não precisam de dados em tempo real)

create materialized view mv_resumo_financeiro_quarto as
select 
	q.NUMERO as numero_quarto,
	q.tipo as tipo_quarto,
	q.tarifa_base_diaria,
	count(distinct r.id) as total_reservas,
	coalesce(sum(p.valor), 0) as receita_total,
	round(
		coalesce(sum(p.valor),0)
		/ nullif(count (distinct r.id),0), 2) as ticket_medio
from quarto as q
left join reserva as r
	on r.numero_quarto = q.NUMERO
left join pagamento as p
	on p.id_reserva = r.id
group by q.NUMERO, q.tipo, q.tarifa_base_diaria
order by receita_total desc;

--refresh materialized view mv_resumo_financeiro_quarto;

-- ==========
-- TRIGGERS
-- ==========

-- TRIGGER 1 (BEFORE): trg_before_reserva_valida_quarto
-- Antes de inserir uma reserva, verifica se o quarto está disponível.
-- o INSERT é cancelado com uma mensagem de erro se o quarto estiver OCUPADO,
-- EM MANUTENÇÃO ou BLOQUEADO.

create or replace function fn_before_reserva_valida_quarto()
returns trigger as $$
declare
	v_status varchar(30);
begin
	select status into v_status
	from quarto
	where NUMERO = new.numero_quarto;

	if v_status <> 'DISPONIVEL' then
		raise exception
			'Quarto % não está disponível par reserva. Status atual: %',
			new.numero_quarto, v_status;
	end if;
	
	return new;
end;
$$ language plpgsql;

create trigger trg_before_reserva_valida_quarto
before insert on reserva for each row
execute function fn_before_reserva_valida_quarto();

-- TRIGGER 2 (AFTER): trg_after_reserva_atualiza_status
-- Depois da inserção de um nova reserva, atualiza automaticamente o status do quarto
-- para 'OCUPADO'

create or replace function fn_after_reserva_atualiza_status()
returns trigger as $$
begin
	update quarto
	set status = 'OCUPADO'
	where NUMERO = new.numero_quarto;

	return new;
end;
$$ language plpgsql;

create trigger trg_after_reserva_atualiza_status
after insert on reserva
for each row execute function fn_after_reserva_atualiza_status();

-- ==========
-- PROCEDURE: sp_finalizar_reserva
-- Encerra uma reserva, liberando o quarto (status --> 'DISPONIVEL')
-- Checkout automático pela data de saída

create or replace procedure sp_finalizar_reserva(p_id_reserva integer)
language plpgsql
as $$
declare
	v_numero_quarto integer;
	v_data_saida date;
begin
	select numero_quarto, data_saida
	into v_numero_quarto, v_data_saida
	from reserva
	where id = p_id_reserva;

if not found then
	raise exception 'Reserva % não encontrada.', p_id_reserva;
end if;

if v_data_saida > current_date then
	raise notice 'Reserva % ainda não encerrou (saída prevista: %). Nenhuma alteração feita.',
		p_id_reserva, v_data_saida;
	return;
end if;
update quarto
set status = 'DISPONIVEL'
where NUMERO = v_numero_quarto;
raise notice 'Reserva % finalizada. Quarto % liberado com sucesso.',
	p_id_reserva, v_numero_quarto;
end;
$$;

CALL sp_finalizar_reserva(1);





