print("***Start Bayesian Network***")

# source("https://bioconductor.org/biocLite.R")
# biocLite(c("bnlearn", "gRain"))

library(bnlearn)
library(Rgraphviz)
library(gRain)

names(windowsFonts())
windowsFonts(mincho=windowsFont("MS Mincho"))
windowsFonts(gothic=windowsFont("MS Gothic"))
par(family="gothic")

#***********************###### IMPORT DATA ######***********************#

recipe_raw <- read.csv("../../db/MixedDB_J.csv", stringsAsFactors=F, header=T, row.names=1)

recipe_raw$道具名  <- factor(recipe_raw$道具名)
#recipe_raw$動作id2 <- factor(recipe_raw$動作id2)
#table(recipe_raw$道具名)
#table(recipe_raw$動作id2)
tool.labels <- factor(recipe_raw$道具名)
#head(recipe_raw)

# make materials
text <- paste(recipe_raw$X1, recipe_raw$X2, recipe_raw$X3, recipe_raw$X4, recipe_raw$X5, recipe_raw$X6, recipe_raw$X7, recipe_raw$X8)
recipe_raw           <- transform(recipe_raw, Materials=text)
recipe_raw$Materials <- as.character(recipe_raw$Materials)
# str(recipe_raw)

Term.All <- unlist(strsplit(text, " "))
Term.All <- Term.All[Term.All != ""]
Term.material <- as.data.frame(Term.All)
Term.material <- as.character(Term.material[!duplicated(Term.material$Term.All), ])

recipeDB <- recipe_raw[, c(15,12,14)]
out      <- c(115,127,128,131,208,222,274,279,285,359)

testNum  <- c(
  12,61,74,137,154,191,194,197,200,220,226,248,271,280,310,318,327,351,366,408
)
withoutTrainNum <- append(out, testNum)

#***********************###### DIFINITION TRAIN DATA######***********************#

material_dtm <- matrix(0, nrow=nrow(recipeDB), ncol=length(Term.material))
colnames(material_dtm) <- Term.material
for(i in 1:nrow(recipeDB)) {
  sentence <- recipeDB[i,1]
  sentence <- unlist(strsplit(sentence, " "))
  sentence <- sentence[sentence != ""]
  for(j in 1:length(sentence)) {
    material_dtm[i,sentence[j]] <- material_dtm[i,sentence[j]] + 1
  }
}

data.train.tool <- material_dtm[-withoutTrainNum, ]
data.train.tool.label <- recipeDB[-withoutTrainNum, "道具名"]
#tool_dtm <- matrix(0, nrow=length(data.train.tool.label), ncol=length(levels(tool.labels)))
#colnames(tool_dtm) <- levels(tool.labels)
#for(i in 1:length(data.train.tool.label)) {
#  tool_dtm[i,data.train.tool.label[i]] <- tool_dtm[i,data.train.tool.label[i]] + 1
#}

#data.train.tool <- cbind(data.train.tool, tool_dtm)

#data.train.tool <- as.data.frame(data.train.tool)
#data.train.tool <- data.frame(lapply(data.train.tool[1:ncol(data.train.tool)], as.factor))
#str(data.train.tool)

#***********************###### FUNCTION() ######***********************#

myStructureLearing <- function(x, y) {
  x2 <- as.data.frame(x)
  lev <- levels(y)
  #term frequency in each category
  ctf <- sapply(lev, function(label) {
    colSums(x[y==label, ])
  }) ## same python
  #ctp <- t(t(ctf) / colSums(ctf)) ## wrong python
  #term propability in each category : p(material | tool)
  structure(list(materialName = names(x2), lev = lev, ctf = ctf), class="myStructureLearing")
}

makeArcsMatrix <- function(model, material) {
  output <- NULL
  for(i in 1:length(material)) {
    for(j in model$lev) {
      if(model$ctf[material[i], j] != 0) {
        output <- rbind(output, matrix(c(material[i], j), ncol=2, byrow=T))
      }
    }
  }
  output <- as.matrix(output)
  colnames(output) <- c("from", "to")
  return(output)
}

#***********************###### CODE : STRUCTURE LEARNING ######***********************#

print("***Start structure learinig***")
model <- myStructureLearing(data.train.tool, data.train.tool.label)
arc.set <- makeArcsMatrix(model, Term.material)

learn.net <- empty.graph(append(model$materialName, model$lev))
arcs(learn.net) <-arc.set
plot(learn.net)

#***********************###### CODE : PARAMETER LEARNING ######***********************#

tool_dtm <- matrix(0, nrow=length(data.train.tool.label), ncol=length(levels(tool.labels)))
colnames(tool_dtm) <- levels(tool.labels)
for(i in 1:length(data.train.tool.label)) {
  tool_dtm[i,data.train.tool.label[i]] <- tool_dtm[i,data.train.tool.label[i]] + 1
}

data <- cbind(data.train.tool, tool_dtm)
data <- as.data.frame(data)
data <- data.frame(lapply(data[1:ncol(data)], as.factor))
head(data)

fitted <- bn.fit(learn.net, as.data.frame(data))
print(fitted$木べら)


#***********************###### CODE : ESTIMATION ######***********************#

#compile(as.grain(fitted), propagate=T)

##gRainによる厳密な推論
#model <- compile(as.grain(fitted), propagate=T)
##Setting evidence
#nodes <- c("塩")
#states <- c("1")

#model.evidence <- setEvidence(model, nodes=nodes, states=states)

#state_predicted <- querygrain(model.evidence, nodes=c("コショウ"), type="marginal", exclude=F)
