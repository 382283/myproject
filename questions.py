#Pythonの特徴
questions = [
    {
        "select_set": "question_0",
        "question": "Pythonの特徴として正しいものを選択してください",
        "options": [
            "コンパイルが不要な言語である",
            "文のグルーピングでは、グループの開始と終了に括弧を用いる",
            "Pythonという名前はニシキヘビの英名が由来である",
            "他のプログラミング言語で書かれたプログラムによる機能拡張には対応していない"
        ],
        "answer": "コンパイルが不要な言語である",
        "explanation": "Pythonはインタプリタ言語のためコンパイルが必要ではありません。"
    },
    {   
        "select_set": "question_0",
        "question": "対話モードの特徴として正しいものを選択してください",
        "options": [
            "行を継続すると正しいインデントが提示される",
            "一次プロンプトは「>>」である",
            "二次プロンプトは「=>」である",
            "プロンプトは、バージョン番号やヘルプコマンドなどの後ろに表示させられる"
        ],
        "answer": "プロンプトは、バージョン番号やヘルプコマンドなどの後ろに表示させられる",
        "explanation": "対話モードでは、入力したプログラムが逐次実行されます。電卓としての用途や簡単なプログラムの動作の確認の際に役立ちます。"
    },
    {   
        "select_set": "question_0",
        "question": "Pythonのソースコードをエンコードするデフォルトの文字コードとして正しいものを選択してください",
        "options": [
            "Shift_JIS",
            "UTF-8",
            "Windows-1252",
            "UTF-16"
        ],
        "answer": "UTF-8",
        "explanation": "PythonのソースコードはUTF-8でエンコードされたものとして扱われます。"
    },
    {   
        "select_set": "question_0",
        "question": "次のコードを実行した結果として正しいものを選択してください".join([
        "x = 42",
        "if x == 0:",
        '    print("xはゼロ")',
        "elif x > 10:",
        '    print("xは10より大きい整数")',
        "elif x < 50:",
        '    print("xは50未満の整数")'
    ]),
        "options": [
            "xはゼロ",
            "xは1より大きい整数",
            "xは10より大きい整数",
            "xは50未満の整数"
        ],
        "answer": "xは10より大きい整数",
        "explanation": "if文の条件評価は上から順番に行われます。x=42のため、`elif x > 10:` が最初に評価され、`xは10より大きい整数`が出力されます。"
    },
    {
        "select_set": "question_1",
        "question": "人工知能の定義は専門家ですら異なる。その説明として適切なものを1つ選べ。",
        "options": [
        "人工知能は学術的な研究分野の1つとして認められていないから",
        "「人工」の解釈が研究者によって異なるから。",
        "「知性」や「知能」の解釈が研究者によって異なるから。",
        "人工知能という言葉は、人工知能研究者ジョン・マッカーシーが彼の論文で指摘に使った言葉だから"],
         "answer": "「知性」や「知能」の解釈が研究者によって異なるから。",
        "explanation": "人工知能の定義に関して、最も多く意見が分かれる点は「知性」や「知能」の解釈です。これが異なるため、人工知能の定義が統一されていません。"
    },
    {
        "select_set": "question_1",
        "question": "人工知能の定義に関するものとして、不適切なものを1つ選べ。",
     "options": [
        "人工知能はは何かについては、専門家の間でも共有されている定義は未だにない",
        "「周囲の状況（入力）によって行動（出力）を帰るエージェント」として人工知能をとらえた場合、あらかじめ単純な振る舞いが決まっている製品も人工知能を搭載した製品だといえる。",
        "同じシステムを指して、それを人工知能だと主張と、それは人工知能ではないと考える人がいてもおかしくない。",
        "知的な処理能力を持つ機械（情報処理システム）であれば、誰もがそれを人工知能であると認めることができる"],
     "answer": "知的な処理能力を持つ機械（情報処理システム）であれば、誰もがそれを人工知能であると認めることができる",
     "explanation": "人工知能の定義には一貫した基準はなく、同じシステムについて異なる意見が生まれやすいです。"
    },
    {
        "select_set": "question_1",
        "question": "機械学習を取り入れた人工知能に関する説明として、最も適しているものを1つ選べ。",
        "options": [
        "サンプルデータが少なくても高い精度で入力と出力の関係を学習する。",
        "制御工学やシステム工学と呼ばれる分野で培われた技術を利用している。",
        "全ての振る舞いがあらかじめ決められている。",
        "パターン認識という古くからの研究をベースにしている。"],
        "answer": "パターン認識という古くからの研究をベースにしている。",
        "explanation": "機械学習は、パターン認識などの古くからある研究に基づいて発展しています。特に大量のデータからパターンを見つけ出し、学習することが重要です。"
    },
    {
        "select_set": "question_1",
        "question": "AI効果の例として、最も適切なものを1つ選べ。",
        "options": [
        "AIを活用したチャットボットと会話していたら、人間と会話しているように感じた。",
        "検索エンジンにはAIが使われているが、その原理が人々に認知されるとAIとは呼ばれなくなった。",
        "青りんごの実物を見たことがなかったが、初めて青いりんごを見たときに青りんごだと認識できた。",
        "AIブームが起こると、家電などの身近なハードウェアがAI搭載を謳うようになった。"],
        "answer": "検索エンジンにはAIが使われているが、その原理が人々に認知されるとAIとは呼ばれなくなった。",
        "explanation": "AI効果とは、AI技術が普及してその原理が認識されると、逆にその技術がAIとして認識されなくなる現象です。"
    }
]


