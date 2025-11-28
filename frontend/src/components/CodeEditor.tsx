import { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import type { CodeEditorProps } from '../types';

export function CodeEditor({ initialCode, language, onChange, readOnly = false, scrollToTaskIndex, todos }: CodeEditorProps) {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  // Scroll to task when selected
  useEffect(() => {
    if (editorRef.current && scrollToTaskIndex !== undefined && todos) {
      const editor = editorRef.current;
      const model = editor.getModel();
      if (!model) return;

      const code = model.getValue();
      const lines = code.split('\n');
      let targetLine = -1;
      let todoCount = 0;

      // Count TODO comments until we reach the Nth one (where N = scrollToTaskIndex)
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const lowerLine = line.toLowerCase();

        // Check if this line contains a TODO comment
        if (lowerLine.includes('todo')) {
          // This is the Nth TODO we're looking for
          if (todoCount === scrollToTaskIndex) {
            targetLine = i + 1; // Monaco uses 1-based line numbers
            break;
          }
          todoCount++;
        }
      }

      if (targetLine > 0) {
        // Scroll to and highlight the line
        editor.revealLineInCenter(targetLine);
        editor.setPosition({ lineNumber: targetLine, column: 1 });

        // Optionally highlight the line temporarily
        const decorations = editor.deltaDecorations([], [
          {
            range: new (window as any).monaco.Range(targetLine, 1, targetLine, 1),
            options: {
              isWholeLine: true,
              className: 'highlight-line',
              glyphMarginClassName: 'highlight-glyph'
            }
          }
        ]);

        // Remove highlight after 2 seconds
        setTimeout(() => {
          editor.deltaDecorations(decorations, []);
        }, 2000);
      }
    }
  }, [scrollToTaskIndex, todos]);

  // Normalize language for Monaco Editor
  const monacoLanguage = language === 'c++' ? 'cpp' : language;

  return (
    <div className="flex h-full flex-col">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold tracking-tight text-black dark:text-foreground">Code Editor</h3>
      </div>
      <div className="h-[750px] overflow-hidden rounded-lg border border-black/5 dark:border-border vercel-shadow">
        <Editor
          height="100%"
          language={monacoLanguage}
          value={initialCode}
          onChange={(value) => onChange(value || '')}
          theme="vs-dark"
          onMount={handleEditorDidMount}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            readOnly: readOnly,
            wordWrap: 'on',
            automaticLayout: true,
            padding: { top: 16, bottom: 16 },
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </div>
  );
}

