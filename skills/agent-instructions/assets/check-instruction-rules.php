<?php

declare(strict_types=1);

$root = (string) getcwd();
$rulesDirectory = getenv('AGENT_INSTRUCTIONS_RULES_DIR') ?: '.ai/rules';
$docsDirectory = getenv('AGENT_INSTRUCTIONS_DOCS_DIR') ?: 'docs';
$docsIndex = getenv('AGENT_INSTRUCTIONS_DOCS_INDEX') ?: $docsDirectory . '/index.md';
$ruleLineBudget = (int) (getenv('AGENT_INSTRUCTIONS_RULE_LINE_BUDGET') ?: 20);

$repositoryFiles = listRepositoryFiles($root);
$failures = [
    ...ruleFailures($root, $repositoryFiles, $rulesDirectory, $ruleLineBudget),
    ...linkFailures($root, $repositoryFiles, [$rulesDirectory, $docsDirectory]),
    ...docsIndexFailures($root, $repositoryFiles, $docsDirectory, $docsIndex),
];

foreach ($failures as $failure) {
    echo PHP_EOL . 'FAIL: ' . $failure . PHP_EOL;
}

exit($failures === [] ? 0 : 1);

/**
 * @return list<string>
 */
function listRepositoryFiles(string $root): array
{
    $output = [];
    $exitCode = 1;

    if (file_exists($root . '/.git')) {
        exec('git ls-files --cached --others --exclude-standard 2>/dev/null', $output, $exitCode);
    }

    if ($exitCode === 0 && $output !== []) {
        return array_values(array_filter($output, fn (string $path): bool => file_exists($root . '/' . $path)));
    }

    $skipped = ['.git', 'vendor', 'node_modules', 'storage', 'public/build'];
    $files = [];
    $iterator = new RecursiveIteratorIterator(
        new RecursiveCallbackFilterIterator(
            new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS),
            fn (SplFileInfo $file): bool => ! in_array(substr($file->getPathname(), strlen($root) + 1), $skipped, true) && ! $file->isLink(),
        ),
    );

    foreach ($iterator as $file) {
        $files[] = substr($file->getPathname(), strlen($root) + 1);
    }

    sort($files);

    return $files;
}

/**
 * @param list<string> $repositoryFiles
 * @return list<string>
 */
function ruleFailures(string $root, array $repositoryFiles, string $rulesDirectory, int $ruleLineBudget): array
{
    if (! is_dir($root . '/' . $rulesDirectory)) {
        return [];
    }

    $failures = [];

    foreach (array_diff(scandir($root . '/' . $rulesDirectory), ['.', '..']) as $entry) {
        $path = $rulesDirectory . '/' . $entry;

        if (is_dir($root . '/' . $path)) {
            $failures[] = "{$path} is a directory. Keep rules flat in {$rulesDirectory}/*.md: Boost only reads the top level.";

            continue;
        }

        if (! str_ends_with($entry, '.md')) {
            continue;
        }

        $contents = (string) file_get_contents($root . '/' . $path);
        $lineCount = substr_count($contents, "\n") + (str_ends_with($contents, "\n") ? 0 : 1);

        if ($lineCount > $ruleLineBudget) {
            $failures[] = "{$path} has {$lineCount} lines, over the {$ruleLineBudget}-line budget per rule. A rule is the trap, the reason and a link; the explanation belongs in the docs section it links to.";
        }

        $globs = rulePaths($contents);

        if ($globs === []) {
            $failures[] = "{$path} has no `paths:` frontmatter. A rule without paths loads in every session: scope it to the files it is about, or make it a standing instruction instead.";

            continue;
        }

        foreach ($globs as $glob) {
            $pattern = globToRegex($glob);

            if (array_filter($repositoryFiles, fn (string $file): bool => preg_match($pattern, $file) === 1) === []) {
                $failures[] = "{$path}: the glob \"{$glob}\" matches no file in the repository. Point it at the files the rule is about, or remove the rule when those files are gone.";
            }
        }
    }

    return $failures;
}

/**
 * @return list<string>
 */
function rulePaths(string $contents): array
{
    if (preg_match('/\A---\n(.*?)\n---\n/s', $contents, $frontmatter) !== 1) {
        return [];
    }

    $globs = [];
    $inPaths = false;

    foreach (explode("\n", $frontmatter[1]) as $line) {
        if (preg_match('/^paths:\s*(.*)$/', $line, $match) === 1) {
            $inline = trim($match[1]);
            $inPaths = $inline === '';

            if (! $inPaths) {
                foreach (explode(',', trim($inline, '[]')) as $value) {
                    $globs[] = trim(trim($value), '"\'');
                }
            }

            continue;
        }

        if ($inPaths && preg_match('/^\s+-\s*(.+)$/', $line, $match) === 1) {
            $globs[] = trim(trim($match[1]), '"\'');

            continue;
        }

        if ($inPaths && trim($line) !== '') {
            $inPaths = false;
        }
    }

    return array_values(array_filter($globs, fn (string $glob): bool => $glob !== ''));
}

function globToRegex(string $glob): string
{
    $regex = '';
    $length = strlen($glob);
    $braceDepth = 0;

    for ($index = 0; $index < $length; $index++) {
        $character = $glob[$index];

        if ($character === '*' && ($glob[$index + 1] ?? '') === '*') {
            $index++;

            if (($glob[$index + 1] ?? '') === '/') {
                $index++;
                $regex .= '(?:.*/)?';
            } else {
                $regex .= '.*';
            }

            continue;
        }

        $braceDepth += match ($character) {
            '{' => 1,
            '}' => -1,
            default => 0,
        };

        $regex .= match ($character) {
            '*' => '[^/]*',
            '?' => '[^/]',
            '{' => '(?:',
            '}' => ')',
            ',' => $braceDepth > 0 ? '|' : ',',
            default => preg_quote($character, '#'),
        };
    }

    return '#\A' . $regex . '\z#';
}

/**
 * @param list<string> $repositoryFiles
 * @param list<string> $directories
 * @return list<string>
 */
function linkFailures(string $root, array $repositoryFiles, array $directories): array
{
    $failures = [];
    $markdownFiles = array_filter(
        $repositoryFiles,
        fn (string $file): bool => str_ends_with($file, '.md')
            && array_filter($directories, fn (string $directory): bool => str_starts_with($file, $directory . '/')) !== [],
    );

    foreach ($markdownFiles as $file) {
        foreach (markdownLinks((string) file_get_contents($root . '/' . $file)) as $target) {
            if (preg_match('#^([a-z][a-z0-9+.-]*:|//)#i', $target) === 1) {
                continue;
            }

            [$targetPath, $anchor] = array_pad(explode('#', $target, 2), 2, null);
            $targetPath = rawurldecode((string) preg_replace('/\?.*$/', '', (string) $targetPath));
            $resolved = $targetPath === '' ? $file : normalisePath(dirname($file) . '/' . $targetPath);

            if ($resolved === null || ! file_exists($root . '/' . $resolved)) {
                $failures[] = "{$file} links to \"{$target}\", which does not exist. Links are relative to the file they are in.";

                continue;
            }

            if ($anchor !== null && $anchor !== '' && str_ends_with($resolved, '.md')
                && ! in_array(strtolower($anchor), markdownAnchors((string) file_get_contents($root . '/' . $resolved)), true)) {
                $failures[] = "{$file} links to \"{$target}\", but {$resolved} has no heading with the anchor #{$anchor}.";
            }
        }
    }

    return $failures;
}

/**
 * @return list<string>
 */
function markdownLinks(string $contents): array
{
    $withoutCode = (string) preg_replace(['/^(```|~~~).*?^\1/ms', '/`[^`\n]*`/'], '', $contents);

    preg_match_all('/(?<!!)\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/', $withoutCode, $matches);

    return $matches[1];
}

/**
 * @return list<string>
 */
function markdownAnchors(string $contents): array
{
    $withoutCode = (string) preg_replace('/^(```|~~~).*?^\1/ms', '', $contents);
    $anchors = [];
    $seen = [];

    preg_match_all('/^#{1,6}\s+(.+?)\s*#*\s*$/m', $withoutCode, $headings);

    foreach ($headings[1] as $heading) {
        $text = (string) preg_replace(['/\[([^\]]*)\]\([^)]*\)/', '/<[^>]+>/'], ['$1', ''], $heading);
        $slug = str_replace(' ', '-', (string) preg_replace('/[^\p{L}\p{N}\p{Mn} _-]/u', '', mb_strtolower($text)));
        $anchors[] = isset($seen[$slug]) ? $slug . '-' . $seen[$slug] : $slug;
        $seen[$slug] = ($seen[$slug] ?? 0) + 1;
    }

    preg_match_all('/<a\s+(?:id|name)="([^"]+)"/i', $contents, $explicit);

    return array_merge($anchors, array_map('strtolower', $explicit[1]));
}

function normalisePath(string $path): ?string
{
    $segments = [];

    foreach (explode('/', $path) as $segment) {
        if ($segment === '' || $segment === '.') {
            continue;
        }

        if ($segment !== '..') {
            $segments[] = $segment;

            continue;
        }

        if ($segments === []) {
            return null;
        }

        array_pop($segments);
    }

    return implode('/', $segments);
}

/**
 * @param list<string> $repositoryFiles
 * @return list<string>
 */
function docsIndexFailures(string $root, array $repositoryFiles, string $docsDirectory, string $docsIndex): array
{
    if (! is_file($root . '/' . $docsIndex)) {
        return [];
    }

    $indexDirectory = dirname($docsIndex);
    $indexed = [];

    foreach (markdownLinks((string) file_get_contents($root . '/' . $docsIndex)) as $target) {
        $path = normalisePath($indexDirectory . '/' . explode('#', $target, 2)[0]);

        if ($path !== null) {
            $indexed[] = rtrim($path, '/');
        }
    }

    $failures = [];

    foreach ($repositoryFiles as $file) {
        if (! str_starts_with($file, $docsDirectory . '/') || ! str_ends_with($file, '.md') || $file === $docsIndex) {
            continue;
        }

        $covered = in_array($file, $indexed, true);

        for ($directory = dirname($file); ! $covered && $directory !== $docsDirectory && $directory !== '.'; $directory = dirname($directory)) {
            $covered = in_array($directory, $indexed, true);
        }

        if (! $covered) {
            $failures[] = "{$file} is not linked from {$docsIndex}. Add a row for it under the subject it belongs to, so agents and people starting at the index find it.";
        }
    }

    return $failures;
}
