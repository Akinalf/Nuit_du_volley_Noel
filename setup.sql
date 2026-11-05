-- ============================================================================
-- Tournoi de volley – base Supabase
-- Lecture publique de l'état du tournoi. Écriture uniquement via save_state() :
--  * joueurs (sans code) : scores de la ronde en cours et des finales, génération
--    de la ronde suivante ; ils ne peuvent ni modifier les noms / horaires, ni
--    remettre à zéro, ni modifier une ronde déjà verrouillée ;
--  * organisateurs (avec le code) : tous les droits.
-- Chaque enregistrement garde l'état précédent dans tournoi_history (300 dernières
-- versions). Remplacer __PIN__ par le code organisateur avant exécution.
-- Script rejouable : relancer ne perd pas les données du tournoi.
-- ============================================================================

create table if not exists public.tournoi_state (
  id         int primary key check (id = 1),
  version    int  not null default 0,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.tournoi_history (
  id       bigserial primary key,
  version  int not null,
  data     jsonb not null,
  saved_at timestamptz not null default now()
);

create table if not exists public.tournoi_secret (
  id           int primary key check (id = 1),
  pin          text not null,
  fails        int  not null default 0,
  locked_until timestamptz
);

alter table public.tournoi_state   enable row level security;
alter table public.tournoi_history enable row level security;
alter table public.tournoi_secret  enable row level security;

drop policy if exists "lecture publique" on public.tournoi_state;
create policy "lecture publique" on public.tournoi_state
  for select to anon, authenticated using (true);

revoke all on public.tournoi_state   from anon, authenticated;
revoke all on public.tournoi_history from anon, authenticated;
revoke all on public.tournoi_secret  from anon, authenticated;
grant select on public.tournoi_state to anon, authenticated;

insert into public.tournoi_state (id) values (1) on conflict (id) do nothing;
insert into public.tournoi_secret (id, pin) values (1, '__PIN__') on conflict (id) do nothing;

-- Vérifie le code organisateur. 8 erreurs d'affilée = blocage d'une minute
-- (ne concerne que l'accès organisateur, jamais la saisie des joueurs).
create or replace function public.check_pin(p_pin text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare s public.tournoi_secret%rowtype;
begin
  select * into s from public.tournoi_secret where id = 1 for update;
  if s.locked_until is not null and s.locked_until > now() then
    return jsonb_build_object('ok', false, 'error', 'Trop d''essais : réessayez dans une minute.');
  end if;
  if s.pin = coalesce(p_pin, '') then
    update public.tournoi_secret set fails = 0, locked_until = null where id = 1;
    return jsonb_build_object('ok', true);
  end if;
  update public.tournoi_secret
     set fails = case when fails + 1 >= 8 then 0 else fails + 1 end,
         locked_until = case when fails + 1 >= 8 then now() + interval '1 minute' else null end
   where id = 1;
  return jsonb_build_object('ok', false, 'error', 'Code incorrect.');
end;
$$;

drop function if exists public.save_state(int, jsonb);

-- Enregistre l'état si personne ne l'a modifié entre-temps (contrôle de version)
-- et si les droits de l'appelant le permettent.
create or replace function public.save_state(p_expected int, p_data jsonb, p_pin text default null)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  oldv int; old jsonb; v int;
  is_admin boolean := false; chk jsonb;
  i int; o jsonb; n jsonb; locked boolean;
  refus constant jsonb := jsonb_build_object('ok', false, 'error', 'Action réservée aux organisateurs.', 'forbidden', true);
begin
  if p_pin is not null and p_pin <> '' then
    chk := public.check_pin(p_pin);
    if not coalesce((chk ->> 'ok')::boolean, false) then
      return chk || jsonb_build_object('auth', true);
    end if;
    is_admin := true;
  end if;

  if p_data is null
     or jsonb_typeof(p_data) is distinct from 'object'
     or length(p_data::text) > 200000
     or coalesce(jsonb_typeof(p_data -> 'teams'), '')  <> 'array'
     or coalesce(jsonb_typeof(p_data -> 'rounds'), '') <> 'array'
     or jsonb_array_length(p_data -> 'teams')  <> 12
     or jsonb_array_length(p_data -> 'rounds') <> 4 then
    return jsonb_build_object('ok', false, 'error', 'Données invalides.');
  end if;

  select version, data into oldv, old from public.tournoi_state where id = 1 for update;
  if oldv is distinct from p_expected then
    return jsonb_build_object('ok', false, 'conflict', true);
  end if;

  -- Droits des joueurs : noms et horaires intacts, aucune ronde existante supprimée,
  -- rondes verrouillées (ronde suivante générée, ou finales commencées) intactes.
  if not is_admin and old ? 'teams' then
    if p_data -> 'teams' is distinct from old -> 'teams'
       or p_data -> 'settings' is distinct from old -> 'settings' then
      return refus;
    end if;
    for i in 0..3 loop
      o := old -> 'rounds' -> i;
      n := p_data -> 'rounds' -> i;
      if jsonb_typeof(o) = 'array' then
        if jsonb_typeof(n) is distinct from 'array' then return refus; end if;
        if i < 3 then
          locked := jsonb_typeof(old -> 'rounds' -> (i + 1)) = 'array';
        else
          locked := coalesce(old -> 'finals', '{}'::jsonb) <> '{}'::jsonb;
        end if;
        if locked and n is distinct from o then return refus; end if;
      end if;
    end loop;
  end if;

  insert into public.tournoi_history (version, data) values (oldv, old);
  delete from public.tournoi_history
   where id <= (select max(id) from public.tournoi_history) - 300;

  update public.tournoi_state
     set data = p_data, version = version + 1, updated_at = now()
   where id = 1
   returning version into v;
  return jsonb_build_object('ok', true, 'version', v);
end;
$$;

revoke all on function public.check_pin(text) from public;
revoke all on function public.save_state(int, jsonb, text) from public;
grant execute on function public.check_pin(text) to anon, authenticated;
grant execute on function public.save_state(int, jsonb, text) to anon, authenticated;
