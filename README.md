# Blender Efficient Modeling

Локальный скилл Codex для создания и проверки моделей и сцен Blender. Основные инструкции находятся в [SKILL.md](SKILL.md); дополнительные материалы читаются по необходимости из `references/`.

## Установка

Разместите этот репозиторий в каталоге скиллов Codex под именем `blender-efficient-modeling`:

```text
~/.codex/skills/blender-efficient-modeling/
  SKILL.md
  agents/
  references/
  scripts/
```

На текущей машине скилл уже установлен в `%USERPROFILE%\.codex\skills\blender-efficient-modeling`. Для работы нужен Blender; Python-скрипты `scripts/blender_asset_runtime.py` и `scripts/inspect_blend.py` запускаются внутри Blender и используют его встроенный `bpy`.

## Использование

В запросе к Codex укажите `$blender-efficient-modeling` или попросите создать модель/сцену в Blender. Скилл направляет работу через один скрипт сборки, проверку результата и повторное открытие `.blend`.

Прямой запуск проверяемой сборки:

```powershell
python .\scripts\run_blender_job.py `
  --build-script .\examples\smoke_build.py `
  --blend .\work\smoke.blend `
  --work-dir .\work\smoke-run `
  --spec .\examples\smoke_spec.json `
  --blender 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
```

`--blender` задаёт путь к установленному Blender; если он совпадает с локальным путём по умолчанию, аргумент можно опустить. Runner считает сборку успешной только после маркера `finalize_job`, сохранения свежего `.blend` и повторного открытия с проверками из `--spec`.

## Проверка пакета

На Windows с Blender 5.2.2 LTS пример из `examples/` собрал сцену, повторно открыл файл и прошёл три проверки: один mesh-объект, его имя и размеры. В репозиторий включены только исходники скилла, документация и этот небольшой пример; результаты сборки и кэш Python исключены через `.gitignore`.
