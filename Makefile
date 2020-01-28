
SLIDES=slides.tex

slides:  ## Compile paper
	pdflatex $(SLIDES)

clean-slides:  ## Clean latex output files
	rm slides.aux slides.log slides.nav slides.out slides.snm slides.toc slides.pdf

clean: clean-slides ## Clean all output files
	@echo cleaning
