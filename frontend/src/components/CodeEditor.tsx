import { useRef } from 'react';
import Editor from '@monaco-editor/react';
import type { CodeEditorProps } from '../types';

export function CodeEditor({ initialCode, language, onChange, readOnly = false }: CodeEditorProps) {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  return (
    <div className="flex h-full flex-col">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold tracking-tight text-black dark:text-foreground">Code Editor</h3>
      </div>
      <div className="h-[600px] overflow-hidden rounded-lg border border-black/5 dark:border-border vercel-shadow">
        <Editor
          height="100%"
          language={language}
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

