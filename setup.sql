-- ============================================================================
-- Tournoi de volley – base Supabase
-- Lecture publique de l'état du tournoi ; écriture uniquement via save_state()
-- avec le code de saisie. Le code n'est jamais lisible depuis la page.
-- Remplacer __PIN__ par le code choisi (ex. 4821) avant exécution.
-- Script rejouable : relancer ne perd pas les données du tournoi.
-- ============================================================================

create table if not exists public.tournoi_state (
  id         int primary key check (id = 1),
  version    int  not null default 0,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.tournoi_secret (
  id           int primary key check (id = 1),
  pin          text not null,
  fails        int  not null default 0,
  locked_until timestamptz
);

alter table public.tournoi_state  enable row level security;
alter table public.tournoi_secret enable row level security;

-- État : lecture seule pour tout le monde. Secret : aucun accès (aucune policy).
drop policy if exists "lecture publique" on public.tournoi_state;
create policy "lecture publique" on public.tournoi_state
  for select to anon, authenticated using (true);

revoke all on public.tournoi_state  from anon, authenticated;
revoke all on public.tournoi_secret from anon, authenticated;
grant select on public.tournoi_state to anon, authenticated;

insert into public.tournoi_state (id) values (1) on conflict (id) do nothing;
insert into public.tournoi_secret (id, pin) values (1, '__PIN__')
  on conflict (id) do update set pin = excluded.pin, fails = 0, locked_until = null;

-- Vérifie le code. 8 erreurs d'affilée = blocage d'une minute (anti force brute).
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

-- Enregistre l'état si le code est bon et si personne n'a modifié entre-temps
-- (contrôle de version : deux arbitres ne s'écrasent jamais l'un l'autre).
create or replace function public.save_state(p_pin text, p_expected int, p_data jsonb)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare chk jsonb; v int;
begin
  chk := public.check_pin(p_pin);
  if not coalesce((chk ->> 'ok')::boolean, false) then
    return chk || jsonb_build_object('auth', true);
  end if;
  if p_data is null or jsonb_typeof(p_data) <> 'object' or length(p_data::text) > 200000 then
    return jsonb_build_object('ok', false, 'error', 'Données invalides.');
  end if;
  update public.tournoi_state
     set data = p_data, version = version + 1, updated_at = now()
   where id = 1 and version = p_expected
   returning version into v;
  if v is null then
    return jsonb_build_object('ok', false, 'conflict', true);
  end if;
  return jsonb_build_object('ok', true, 'version', v);
end;
$$;

revoke all on function public.check_pin(text) from public;
revoke all on function public.save_state(text, int, jsonb) from public;
grant execute on function public.check_pin(text) to anon, authenticated;
grant execute on function public.save_state(text, int, jsonb) to anon, authenticated;
