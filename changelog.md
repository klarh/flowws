# v0.6.0 - 2024/01/10

## Added

- `flowws.exit_stack` element to scopes inside `Workflow.run()`
- Expose workflow using `flowws.workflow` key in addition to just `workflow`

# v0.5.3 - 2023/12/06

## Fixed

- Fix ignored files in version control (.gitignore)

# v0.5.2 - 2022/08/16

## Fixed

- Fix mutation of input scope in `Workflow.from_JSON()`

# v0.5.1 - 2022/04/29

## Fixed

- Fix module serialization

# v0.5.0 - 2022/04/01

## Added

- `register_module` function for easier notebook or REPL development
- Use fully-qualified module name when saving workflows to JSON

## Fixed

- Catch OSError in `try_to_import`

# v0.4.0 - 2020/06/24

## Added
- Workflow.run() now returns the final scope object
- Shallow copies of Scope objects support callbacks

# v0.3.0 - 2020/05/05

## Added
- Made `Workflow` constructor simply create a `DirectoryStorage` in the current working directory by default

# v0.2.2 - 2020/03/27

## Fixed
- Made `Stage` objects use a copy of default arguments

# v0.2.1 - 2020/02/06

## Fixed
- Parsing for bool-type arguments
- Fixed and clarified behavior of `Scope` for registered callbacks

# v0.2.0 - 2020/02/05

## Added
- Reference to the current workflow in the currently-used scope
- `Stage.arg_specifications` and `Stage.arg_specification_list`
- `Range` and `Argument.valid_values`
- `Scope` and `Scope.set_call()`
- `try_to_import()` helper function

# v0.1.0 - 2019/06/25

## Added
- `Argument`
- `Stage`
- `Storage` (`GetarStorage`, `DirectoryStorage`)
- `Workflow`
