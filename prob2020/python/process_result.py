"""This module processes the result of running probabilistic 20/20 by
converting lists into a formatted dataframe."""
import prob2020.python.utils as utils
import prob2020.python.p_value as mypval
import numpy as np
import pandas as pd

def handle_tsg_results(permutation_result):
    """Handles result from TSG results.

    Takes in output from multiprocess_permutation function and converts to
    a better formatted dataframe.

    Parameters
    ----------
    permutation_result : list
        output from multiprocess_permutation

    Returns
    -------
    permutation_df : pd.DataFrame
        formatted output suitable to save
    """
    permutation_df = pd.DataFrame(sorted(permutation_result, key=lambda x: x[2]),
                                  columns=['gene', 'inactivating count', 'inactivating p-value',
                                           'Total SNV Mutations', 'SNVs Unmapped to Ref Tx'])
    permutation_df['inactivating p-value'] = permutation_df['inactivating p-value'].astype('float')
    tmp_df = permutation_df[permutation_df['inactivating p-value'].notnull()]

    # get benjamani hochberg adjusted p-values
    permutation_df['inactivating BH q-value'] = np.nan
    permutation_df['inactivating BH q-value'][tmp_df.index] = mypval.bh_fdr(tmp_df['inactivating p-value'])

    # sort output by p-value. due to no option to specify NaN order in
    # sort, the df needs to sorted descendingly and then flipped
    permutation_df = permutation_df.sort(columns='inactivating p-value', ascending=False)
    permutation_df = permutation_df.reindex(index=permutation_df.index[::-1])

    # order result
    permutation_df = permutation_df.set_index('gene', drop=False)
    col_order  = ['gene', 'Total SNV Mutations', 'SNVs Unmapped to Ref Tx',
                  #'Total Frameshift Mutations', 'Frameshifts Unmapped to Ref Tx',
                  'inactivating count', 'inactivating p-value',
                  'inactivating BH q-value']
    return permutation_df[col_order]


def handle_oncogene_results(permutation_result, non_tested_genes, num_permutations):
    """Takes in output from multiprocess_permutation function and converts to
    a better formatted dataframe.

    Parameters
    ----------
    permutation_result : list
        output from multiprocess_permutation

    Returns
    -------
    permutation_df : pd.DataFrame
        formatted output suitable to save
    """
    mycols = ['gene', 'num recurrent', 'position entropy',
              'delta position entropy', 'mean vest score',
              'recurrent p-value', 'entropy p-value',
              'delta entropy p-value', 'vest p-value',
              'Total Mutations', 'Unmapped to Ref Tx']
    permutation_df = pd.DataFrame(permutation_result, columns=mycols)

    # get benjamani hochberg adjusted p-values
    permutation_df['recurrent BH q-value'] = mypval.bh_fdr(permutation_df['recurrent p-value'])
    permutation_df['entropy BH q-value'] = mypval.bh_fdr(permutation_df['entropy p-value'])
    permutation_df['delta entropy BH q-value'] = mypval.bh_fdr(permutation_df['delta entropy p-value'])
    permutation_df['vest BH q-value'] = mypval.bh_fdr(permutation_df['vest p-value'])

    # combine p-values
    permutation_df['tmp entropy p-value'] = permutation_df['entropy p-value']
    permutation_df['tmp vest p-value'] = permutation_df['vest p-value']
    permutation_df.loc[permutation_df['entropy p-value']==0, 'tmp entropy p-value'] = 1. / num_permutations
    permutation_df.loc[permutation_df['vest p-value']==0, 'tmp vest p-value'] = 1. / num_permutations
    permutation_df['combined p-value'] = permutation_df[['entropy p-value', 'vest p-value']].apply(mypval.fishers_method, axis=1)
    permutation_df['combined BH q-value'] = mypval.bh_fdr(permutation_df['combined p-value'])
    del permutation_df['tmp vest p-value']
    del permutation_df['tmp entropy p-value']

    # include non-tested genes in the result
    #no_test_df = pd.DataFrame(index=range(len(non_tested_genes)))
    #no_test_df['Performed Recurrency Test'] = 0
    #no_test_df['gene'] = non_tested_genes
    #permutation_df = pd.concat([permutation_df, no_test_df])
    #permutation_df['Performed Recurrency Test'] = permutation_df['Performed Recurrency Test'].fillna(1).astype(int)

    # order output
    permutation_df = permutation_df.set_index('gene', drop=False)  # make sure genes are indices
    permutation_df['num recurrent'] = permutation_df['num recurrent'].fillna(-1).astype(int)  # fix dtype isssue
    col_order = ['gene', 'Total Mutations', 'Unmapped to Ref Tx',
                 'num recurrent', 'position entropy',
                 'delta position entropy', 'mean vest score',
                 'recurrent p-value', 'recurrent BH q-value', 'entropy p-value',
                 'vest p-value', 'combined p-value', 'entropy BH q-value', 'delta entropy p-value',
                 'delta entropy BH q-value', 'vest BH q-value', 'combined BH q-value']
                 #'Performed Recurrency Test']
    permutation_df = permutation_df.sort(columns=['combined p-value'])
    return permutation_df[col_order]


def handle_protein_results(permutation_result, non_tested_genes, num_permutations):
    """Takes in output from multiprocess_permutation function and converts to
    a better formatted dataframe.

    Parameters
    ----------
    permutation_result : list
        output from multiprocess_permutation

    Returns
    -------
    permutation_df : pd.DataFrame
        formatted output suitable to save
    """
    mycols = ['gene', 'normalized graph-smoothed position entropy',
              'normalized graph-smoothed postion entropy p-value', 'Total Mutations', 'Unmapped to Ref Tx']
    permutation_df = pd.DataFrame(permutation_result, columns=mycols)

    # get benjamani hochberg adjusted p-values
    permutation_df['normalized graph-smoothed position entropy BH q-value'] = mypval.bh_fdr(permutation_df['normalized graph-smoothed position entropy p-value'])

    # order output
    permutation_df = permutation_df.set_index('gene', drop=False)  # make sure genes are indices
    col_order = ['gene', 'Total Mutations', 'Unmapped to Ref Tx',
                 'normalized graph-smoothed position entropy',
                 'normalized graph-smoothed position entropy p-value',
                 'normalized graph-smoothed position entropy BH q-value']
    permutation_df = permutation_df.sort(columns=['normalized graph-smoothed position entropy p-value'])
    return permutation_df[col_order]


def handle_effect_results(permutation_result):
    """Takes in output from multiprocess_permutation function and converts to
    a better formatted dataframe.

    Parameters
    ----------
    permutation_result : list
        output from multiprocess_permutation

    Returns
    -------
    permutation_df : pd.DataFrame
        formatted output suitable to save
    """
    mycols = ['gene', 'num recurrent', 'num inactivating', 'entropy-on-effect',
              'entropy-on-effect p-value',
              'Total Mutations', 'Unmapped to Ref Tx']
    permutation_df = pd.DataFrame(sorted(permutation_result, key=lambda x: x[4]),
                                  columns=mycols)

    # get benjamani hochberg adjusted p-values
    permutation_df['entropy-on-effect BH q-value'] = mypval.bh_fdr(permutation_df['entropy-on-effect p-value'])

    # order output
    permutation_df = permutation_df.set_index('gene', drop=False)  # make sure genes are indices
    permutation_df['num recurrent'] = permutation_df['num recurrent'].fillna(-1).astype(int)  # fix dtype isssue
    col_order = ['gene', 'Total Mutations', 'Unmapped to Ref Tx',
                 'num recurrent', 'num inactivating', 'entropy-on-effect',
                 'entropy-on-effect p-value', 'entropy-on-effect BH q-value']
    return permutation_df[col_order]

