-- ============================================================================
-- Tournoi de volley – base Supabase (version sans code de saisie)
-- Lecture publique de l'état du tournoi ; écriture uniquement via save_state().
-- Chaque enregistrement conserve l'état précédent dans tournoi_history
-- (300 dernières versions) pour pouvoir tout restaurer en cas d'erreur.
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

alter table public.tournoi_state   enable row level security;
alter table public.tournoi_history enable row level security;

-- État : lecture seule pour tout le monde. Historique : aucun accès depuis la page.
drop policy if exists "lecture publique" on public.tournoi_state;
create policy "lecture publique" on public.tournoi_state
  for select to anon, authenticated using (true);

revoke all on public.tournoi_state   from anon, authenticated;
revoke all on public.tournoi_history from anon, authenticated;
grant select on public.tournoi_state to anon, authenticated;

insert into public.tournoi_state (id) values (1) on conflict (id) do nothing;

-- Enregistre l'état si personne ne l'a modifié entre-temps (contrôle de version :
-- deux personnes ne s'écrasent jamais l'une l'autre) et si sa structure est valide.
create or replace function public.save_state(p_expected int, p_data jsonb)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare oldv int; old jsonb; v int;
begin
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

revoke all on function public.save_state(int, jsonb) from public;
grant execute on function public.save_state(int, jsonb) to anon, authenticated;
