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
