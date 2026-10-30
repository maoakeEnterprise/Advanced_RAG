PYTHON = uv run python

# manage the unzip file
DATA_ZIP = vllm-0.10.1.zip
RAW_DIR = data/raw
DATA_NAME = $(basename $(DATA_ZIP))

GREEN = \033[32m
RED   = \033[31m
BOLD  = \033[1m
DIM   = \033[2m
RESET = \033[0m


.PHONY: unzip_data install clean


unzip_data: $(RAW_DIR)/$(DATA_NAME)

$(RAW_DIR)/$(DATA_NAME): $(DATA_ZIP)
	mkdir -p $(RAW_DIR)
	unzip -o -q $(DATA_ZIP) -d $(RAW_DIR)
	touch $@
	@printf "\n$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n"
	@printf "$(BOLD)$(GREEN)              ✔  UNZIP DONE$(RESET)\n"
	@printf "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n"
	@printf "   $(DIM)Archive  $(RESET) %s\n" "$(DATA_ZIP)"
	@printf "   $(DIM)Dossier  $(RESET) %s\n" "$@"
	@printf "   $(DIM)Fichiers $(RESET) %s\n" "$$(find $@ -type f | wc -l)"
	@printf "   $(DIM)Taille   $(RESET) %s\n" "$$(du -sh $@ | cut -f1)"
	@printf "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n\n"

install:
	uv sync

clean:
	rm -rf $(RAW_DIR)
	@printf "\n$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n"
	@printf "$(BOLD)$(GREEN)              ✔  CLEAN DONE$(RESET)\n"
	@printf "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n"
