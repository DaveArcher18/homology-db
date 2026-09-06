# Contributing

Thank you for helping make the atlas clearer and more trustworthy. Small
contributions are welcome, including questions, reading feedback, citations,
and mathematical corrections. You do not need to understand the entire project.

## Pick a starting point

- **Confusing page or bug:** open a website bug report with the page link,
  what you expected, what happened, and reproduction steps.
- **Mathematical correction:** use the feedback link on the affected space.
  Include coefficients, degrees, conventions, and a source or argument.
- **Human family review:** choose **Review this result** on the workbench.
  Reviewing just one instance or coefficient is useful.
- **New example:** use the request-a-space form. A good citation is a great start.
- **Code or documentation:** a focused pull request is welcome; discuss larger
  changes in an issue first so we can agree on scope.

The [issue chooser](https://github.com/DaveArcher18/homology-db/issues/new/choose)
has the available forms. GitHub submissions are public: omit credentials,
private correspondence, and other people's personal information.

## A small pull request

1. Fork the repository and create a branch for one change.
2. Follow the [development guide](docs/DEVELOPMENT.md).
3. Explain the problem and the smallest useful change.
4. Run the relevant tests and include their results. Say when a check could
   not run; a skipped test is not a passing test.
5. For a visual change, include a narrow-screen screenshot and check keyboard
   use. For a mathematical change, include the exact source and scope.

Edit source files rather than hand-editing the generated `dist/atlas.html`.
For ordinary source PRs, leave rebuilding the release artifact to the maintainer
unless agreed otherwise. The artifact binds an exact source commit, so it must
be rebuilt after any merge that changes that identity.

## Mathematical care

- Never replace “not recorded” with zero.
- Keep sources, derivations, parameter ranges, and reduced/unreduced conventions
  explicit. Distinguish a proposed computation from one actually performed.
- Preserve stable links and existing records. Corrections should retain history.
- Do not mark a result human-reviewed because tests passed or an agent checked it.
- Cite a book's theorem/example and page, or a paper's precise location.
  Link to sources rather than copying material you do not have permission to
  redistribute.

The [human-review guide](docs/reviews/FAMILY_REVIEW_GUIDE.md) explains scoped
verdicts and maintainer validation. Its detailed schema is for recording reviews;
you do not need to edit JSON just to report a problem.

## Working together

Be welcoming to beginners, assume good intent, and critique claims rather than
people. Explain unfamiliar notation, give credit, and avoid hostile or
discriminatory language. Disagreement about mathematics is welcome when it is
specific and supported.

AI-assisted contributions are welcome. Explain which checks were actually run
and identify any uncertainty. You remain responsible for understanding the
change; generated text is not a human mathematical review.

This is a side project, with no promised response time. A reproducible small
issue is usually easier to act on than a broad rewrite.

## Licensing and security

The original-code license decision is still pending; see
[licensing status](docs/LICENSING.md). Please discuss substantial code or data
contributions before relying on a licensing assumption. Retain all upstream
attribution and license notices.

For sensitive vulnerabilities, follow [SECURITY.md](SECURITY.md), not a public
issue containing exploit details or private data.
