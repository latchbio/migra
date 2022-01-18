import re

class Formatter:

    def __init__(self, eager_parens=True, destructive_func_replace=True) -> None:
        # add other format wide configs
        self.eager_parens = eager_parens
        self.destructive_func = destructive_func_replace


    def create_policy(self, all_changes):
        if self.eager_parens:
            # only fails on check true params, so hard coding is ok
            for i, change in enumerate(all_changes):
                all_changes[i] = re.sub(r'with\s+check\s+true', 'with check (true)', change, flags=re.IGNORECASE)
        return all_changes

    def prepend_drops_for_replacements(self, all_changes: list) -> list:
        drops = []
        if self.destructive_func:
            for change in all_changes:
                matches = re.search(r'CREATE\s+OR\s+REPLACE\s+FUNCTION\s+([^\)]+)', change, flags=re.IGNORECASE)
                if matches:
                    drop = f'\ndrop function if exists {matches.group(1)});\n'
                    drops.append(drop)
        return drops + all_changes
    
if __name__ == '__main__':
    # sanity checks
    f = Formatter()
    out = f.create_policy(["""
        create policy "ribosome2"
        on "app_public"."ldata_wf_ex"
        as permissive
        for all
        to postgres
        using (true)
        with check true;
    """])
    assert out == ["""
        create policy "ribosome2"
        on "app_public"."ldata_wf_ex"
        as permissive
        for all
        to postgres
        using (true)
        with check (true);
    """], out

    out = f.create_policy(["""
        create policy "ribosome2"
        on "app_public"."ldata_wf_ex"
        as permissive
        for all
        to postgres
        using (true)
        with check (true);
    """])
    assert out == ["""
        create policy "ribosome2"
        on "app_public"."ldata_wf_ex"
        as permissive
        for all
        to postgres
        using (true)
        with check (true);
    """], out

    assert len(f.prepend_drops_for_replacements(["""
    CREATE OR REPLACE FUNCTION public.test_func_1(len_from integer, len_to integer)
 RETURNS text
 LANGUAGE plpgsql
AS $function$
declare
   film_count integer;
begin
end;
$function$
;
    """])) == 2
