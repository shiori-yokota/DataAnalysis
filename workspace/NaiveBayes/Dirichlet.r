cat("***Start Bayesian Network***\n")

# source("https://bioconductor.org/biocLite.R")
# biocLite(c("bnlearn", "gRain"))

library(bnlearn)
library(Rgraphviz)

names(windowsFonts())
windowsFonts(mincho=windowsFont("MS Mincho"))
windowsFonts(gothic=windowsFont("MS Gothic"))
par(family="gothic")

#***********************###### IMPORT DATA ######***********************#

recipe <- read.csv("../../db/MixedDB.csv", stringsAsFactors=F, header=T, row.names=1)

#recipe_raw <- recipe[c(1,2,8,18), ]
recipe_raw <- recipe

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

write.table(material_dtm, "../../db/Ingredients.txt", quote=F, row.names=F, append=F)

data.train.tool <- material_dtm[-withoutTrainNum, ]
data.train.tool.label <- recipeDB[-withoutTrainNum, "道具名"]

#***********************###### FUNCTION() ######***********************#

myStructureLearing <- function(x, y) {
  x2 <- as.data.frame(x)
  lev <- levels(y)
  #term frequency in each category
  ctf <- sapply(lev, function(label) {
    colSums(x[y==label, ])
  }) ## same python
  #term propability in each category : p(material | tool)
  structure(list(materialName = names(x2), lev = lev, ctf = ctf), class="bn")
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

myfit <- function(x, data, method) {
  
  fit <- function(node) {
    parents <- x$nodes[[node]]$parents
    children <- x$nodes[[node]]$children
    
    cat("* fitting parameters of node", node, "(discrete).\n")
    if (length(parents) > 0)
      cat("  > found parents:", parents, "\n")
    
    print(data[, c(node, parents)])
    
    if (method == "mle") {
      tab = table(data[, c(node, parents), drop = FALSE]) #count of 0 and 1
      cat("count")
      print(tab)
    }
    else { #method == bayes#
      tab = table(data[, c(node, parents), drop = FALSE]) #count of 0 and 1
      print("count")
      print(tab)
      tab = tab + 1 / prod(dim(tab))
      cat("dirichlet")
      print(tab)
    }
    
    margin = seq(length(parents) + 1)[-1]
    print(margin) #marginの値
    tab = prop.table(tab, margin) #集計
    print(tab)

    class = ifelse(is(data[, node], "ordered"), "bn.fit.onode", "bn.fit.dnode")
    structure(list(node = node, parents = parents, children = children,
                   prob = tab), class = class)
    
  }
  
  fitted = sapply(names(x$nodes), fit, simplify = FALSE)
  orig.class = class(x)
  class = c(orig.class[orig.class != "bn"], "bn.fit")
  
  # preserve the training node label from Bayesian network classifiers.
  if (x$learning$algo %in% classifiers) # is.element(x$learning$algo, classifiers)
    fitted = structure(fitted, class = class, training = x$learning$args$training)
  else
    fitted = structure(fitted, class = class)
  
  return(fitted)
}

#***********************###### CODE : STRUCTURE LEARNING ######***********************#

cat("***Start structure learinig***\n")
model <- myStructureLearing(data.train.tool, data.train.tool.label)
arc.set <- makeArcsMatrix(model, Term.material)


learn.net <- empty.graph(append(model$materialName, model$lev))
arcs(learn.net) <-arc.set
graphviz.plot(learn.net, shape="ellipse")
#plot(learn.net)


#***********************###### CODE : PARAMETER LEARNING ######***********************#

tool_dtm <- matrix(0, nrow=length(data.train.tool.label), ncol=length(levels(tool.labels)))
colnames(tool_dtm) <- levels(tool.labels)
for(i in 1:length(data.train.tool.label)) {
  tool_dtm[i,data.train.tool.label[i]] <- tool_dtm[i,data.train.tool.label[i]] + 1
}
tmp.data.train.tool <- cbind(data.train.tool, tool_dtm)
# convert discrete data
tmp.data.train.tool <- tmp.data.train.tool >= 1
tmp.data.train.tool <- as.data.frame(tmp.data.train.tool)
tmp.data.train.tool <- data.frame(lapply(tmp.data.train.tool[1:ncol(tmp.data.train.tool)], as.factor))
#str(tmp.data.train.tool)

fitted <- bn.fit(learn.net, tmp.data.train.tool, method = "mle", debug=T)
cat("MLE\n")
#fitted_mle <- myfit(learn.net, tmp.data.train.tool, method="mle")
#print("BAYES")
#fitted_bayes <- myfit(learn.net, tmp.data.train.tool, method="bayes")

#***********************###### CODE : SAMPLE ######***********************#

#model2 <- compile(as.grain(fitted), propagate=T)
##Setting evidence
#nodes <- model$materialName
#states <- c("0","0","1","0","0","0","1","0","0")

#model.evidence <- setEvidence(model2, nodes=nodes, states=states)

#state_predicted <- querygrain(model.evidence, nodes=levels(tool.labels), type="marginal", exclude=F)
#print(state_predicted)


#***********************###### CODE : SAMPLE ######***********************#

# step1
#res <- hc(data.train.tool, score='bic', debug=F, max.iter=100000)
#res <- drop.arc(res, "しらす", "ごはん")
#print(res)
#plot(res)
# step2
#fitted <- bn.fit(res, data.train.tool, method='bayes')


##gRainによる厳密な推論
#model <- compile(as.grain(fitted), propagate=T)
##Setting evidence
#nodes <- c("塩")
#states <- c("1")

#model.evidence <- setEvidence(model, nodes=nodes, states=states)

#state_predicted <- querygrain(model.evidence, nodes=c("コショウ"), type="marginal", exclude=F)
