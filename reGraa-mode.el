;; reGraa mode - (c)2015 by Niklas Reppel (nik@parkellipsen.de)

;; Drew heavy inspiration from Alex McLean's tidal-mode, and its
;; predecessors (even though this has not much to do with haskell ...)

(require 'scheme)
(require 'comint)
(require 'thingatpt)
(require 'find-lisp)
(require 'pulse)

(defvar reGraa-events
  '("snd1" "snd2" "snd3" "snd4" "snd5" "snd6" "snd7" "snd8" "buzz" "sine" "pluck" "akita" "midi" "say" "sqr" "risset" "sample"))

(defvar reGraa-keywords
      '("chance" "rand" "just" "loop" "seq" "graph" "map" "chance_map"))

(defvar reGraa-font-lock-defaults
  `((
     ;; stuff between "
     ("\"\\.\\*\\?" . font-lock-string-face)
     ;; ; : , ; { } =>  @ $ = are all special elements
     ("-\\|:\\|,\\|<\\|>\\||\\|$\\|=" . font-lock-keyword-face)
     ( ,(regexp-opt reGraa-keywords 'words) . font-lock-builtin-face)
     ( ,(regexp-opt reGraa-events 'words) . font-lock-constant-face)
)))

(defvar reGraa-tab-width nil "Width of a tab for reGraa mode")

(defvar reGraa-buffer
  "*reGraa*"
  "*The name of the reGraa process buffer (default=*reGraa*).")

(defvar reGraa-interpreter
  "python"
  "*The reGraa interpeter to use .")

(defvar reGraa-interpreter-arguments
  (list ""
        )
  "*Arguments to the reGraa interpreter (default=none).")

(defun reGraa-buffer-filter (proc string)
  (unless (string-match "[:space:]reGraa>[:space:]" string) 
  (setq reGraa-output string))
  (when (buffer-live-p (process-buffer proc))
    (with-current-buffer (process-buffer proc)
      (let ((moving (= (point) (process-mark proc))))
	(save-excursion
	  ;; Insert the text, advancing the process marker.
	  (goto-char (process-mark proc))
	  (insert string)	  
	  (set-marker (process-mark proc) (point)))
	(if moving (goto-char (process-mark proc))))))
)

(defun reGraa-start ()
  "Start reGraa."
  (interactive)
  (if (comint-check-proc reGraa-buffer)
      (error "A reGraa process is already running")
    (apply
     'make-comint
     "reGraa"
     reGraa-interpreter
     nil)
    (reGraa-send-string "import sys")
    (reGraa-send-string (concat "sys.path.append(\"" reGraa-path "\")"))
    (reGraa-send-string "from regraa import *")
    ;(reGraa-send-string "start_reGraa()")    
    (reGraa-see-output)
    (set-process-filter (get-buffer-process reGraa-buffer) 'reGraa-buffer-filter)
    )
  )

(defun reGraa-see-output ()
  "Show python output."
  (interactive)
  (when (comint-check-proc reGraa-buffer)
    (delete-other-windows)
    (split-window-horizontally)    
    (with-current-buffer reGraa-buffer
      (let ((window (display-buffer (current-buffer))))       
	(goto-char (point-max))
	(save-selected-window
	  (set-window-point window (point-max))
	  )
	)   
      )
    ;(select-window (get-buffer-window reGraa-buffer))
    ;(split-window-vertically)
    
   )
)

(defun reGraa-quit ()
  "Quit reGraa."
  (interactive)
  (reGraa-send-string "akita_quit()")
  (kill-buffer reGraa-buffer)
  (delete-other-windows))

(defun chunk-string (n s)
  "Split a string into chunks of 'n' characters."
  (let* ((l (length s))
         (m (min l n))
         (c (substring s 0 m)))
    (if (<= l n)
        (list c)
      (cons c (chunk-string n (substring s n))))))

(defun reGraa-send-string (s)
  (if (comint-check-proc reGraa-buffer)
      (let ((cs (chunk-string 64 (concat s "\n"))))
        (mapcar (lambda (c) (comint-send-string reGraa-buffer c)) cs))
    (error "no reGraa process running?")))

(defun reGraa-run-line ()
  "Send the current line to the interpreter."
  (interactive)
  (let* ((s (buffer-substring (line-beginning-position)
			      (line-end-position)))
	 )
    (reGraa-send-string s))
  (pulse-momentary-highlight-one-line (point))
  (next-line)
  )


(defun reGraa-run-multiple-lines ()
  "Send the current region to the interpreter as a single line."
  (interactive)
  (save-excursion
   (mark-paragraph)
   (let* ((s (buffer-substring-no-properties (region-beginning)
                                             (region-end)))
          )
     (reGraa-send-string s)     
     (mark-paragraph)
     (pulse-momentary-highlight-region (mark) (point))
     )
    )
  )


(defun reGraa-interrupt ()
  (interactive)
  (if (comint-check-proc reGraa-buffer)
      (with-current-buffer reGraa-buffer
	(interrupt-process (get-buffer-process (current-buffer))))
    (error "no reGraa process running?")))

(defvar reGraa-mode-map nil
  "reGraa keymap.")

(defun reGraa-mode-keybindings (map)
  "ReGraa keybindings."
  (define-key map [?\C-c ?\C-s] 'reGraa-start)
  (define-key map [?\C-c ?\C-v] 'reGraa-see-output)
  (define-key map [?\C-c ?\C-q] 'reGraa-quit)
  (define-key map [?\C-c ?\C-c] 'reGraa-run-line)  
  (define-key map [?\C-c ?\C-a] 'reGraa-run-multiple-lines)
  (define-key map (kbd "<C-return>") 'reGraa-run-multiple-lines)
  (define-key map [?\C-c ?\ä] 'reGraa-run-multiple-lines)
  (define-key map [?\C-c ?\C-i] 'reGraa-interrupt)
  )

(defun turn-on-reGraa-keybindings ()
  "ReGraa keybindings in the local map."
  (local-set-key [?\C-c ?\C-s] 'reGraa-start)
  (local-set-key [?\C-c ?\C-v] 'reGraa-see-output)
  (local-set-key [?\C-c ?\C-q] 'reGraa-quit)
  (local-set-key [?\C-c ?\C-c] 'reGraa-run-line)
  (local-set-key [?\C-c ?\C-a] 'reGraa-run-multiple-lines)
  (local-set-key (kbd "<C-return>") 'reGraa-run-multiple-lines)
  (local-set-key [?\C-c ?\ä] 'reGraa-run-multiple-lines)  
  (local-set-key [?\C-c ?\C-i] 'reGraa-interrupt)
  )

(defun reGraa-mode-menu (map)
  "ReGraa menu."
  (define-key map [menu-bar reGraa]
    (cons "ReGraa" (make-sparse-keymap "ReGraa")))
  (define-key map [menu-bar reGraa expression run-multiple-lines]
    '("Run multiple lines" . reGraa-run-multiple-lines))
  (define-key map [menu-bar reGraa expression run-line]
    '("Run line" . reGraa-run-line))
  (define-key map [menu-bar reGraa quit-reGraa]
    '("Quit reGraa" . reGraa-quit))
  (define-key map [menu-bar reGraa see-output]
    '("See output" . reGraa-see-output))
  (define-key map [menu-bar reGraa start]
    '("Start reGraa" . reGraa-start)))

(if reGraa-mode-map
    ()
  (let ((map (make-sparse-keymap "ReGraa")))
    (reGraa-mode-keybindings map)
    (reGraa-mode-menu map)
    (setq reGraa-mode-map map)))

(define-derived-mode
  reGraa-mode
  fundamental-mode
  "ReGraa"
  "Major mode for interacting with an inferior reGraa process."
  (electric-pair-mode)
  (setq font-lock-defaults reGraa-font-lock-defaults)
  ;(set (make-local-variable 'paragraph-start) "\f\\|[ \t]*$")
  ;(set (make-local-variable 'paragraph-separate) "[ \t\f]*$")					
  )

;; you again used quote when you had '((mydsl-hilite))
;; I just updated the variable to have the proper nesting (as noted above)
;; and use the value directly here
(setq font-lock-defaults reGraa-font-lock-defaults)

;; when there's an override, use it
;; otherwise it gets the default value
(when reGraa-tab-width
  (setq tab-width reGraa-tab-width))

;; for comments
;; overriding these vars gets you what (I think) you want
;; they're made buffer local when you set them
(setq comment-start "#")
(setq comment-end "")

(modify-syntax-entry ?# "< b" reGraa-mode-syntax-table)
(modify-syntax-entry ?\n "> b" reGraa-mode-syntax-table)

(add-to-list 'auto-mode-alist '("\\.reGraa$" . reGraa-mode))

(provide 'reGraa-mode)
